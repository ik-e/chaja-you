/** Same-origin canvas Viewer. Grants live only in the first WebSocket message. */
const handles = new WeakMap();

export function mount(container, grant, onEvent = () => {}) {
  if (!(container instanceof HTMLElement) || !grant ||
      typeof grant.viewer_grant !== 'string' || !Number.isInteger(grant.generation)) {
    throw new TypeError('A container and AuthGrant are required');
  }
  handles.get(container)?.dispose();
  const canvas = document.createElement('canvas');
  canvas.tabIndex = 0;
  canvas.setAttribute('aria-label', '원격 인증 화면');
  canvas.style.maxWidth = '100%';
  container.append(canvas);
  const url = new URL('/remote/viewer/ws', location.origin);
  url.protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
  const socket = new WebSocket(url);
  const controller = new AbortController();
  let disposed = false;
  let inputEnabled = false;
  let ready = false;
  let frameVersion = 0;
  let pendingGrant = grant;
  grant = null;

  function send(message) {
    if (!disposed && inputEnabled && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(message));
    }
  }

  function dispose() {
    if (disposed) return;
    disposed = true;
    inputEnabled = false;
    pendingGrant = null;
    frameVersion++;
    controller.abort();
    socket.onopen = socket.onmessage = socket.onerror = socket.onclose = null;
    socket.close();
    canvas.remove();
    if (handles.get(container) === handle) handles.delete(container);
  }
  const handle = { dispose };
  handles.set(container, handle);
  socket.onopen = () => {
    socket.send(JSON.stringify({ t: 'attach', grant: pendingGrant }));
    pendingGrant = null;
  };
  socket.onmessage = (event) => {
    if (disposed) return;
    let message;
    try { message = JSON.parse(event.data); }
    catch { onEvent('error'); dispose(); return; }
    if (message.t === 'status') {
      inputEnabled = message.state === 'human';
      if (inputEnabled && !ready) { ready = true; onEvent('ready'); }
      return;
    }
    if (message.t === 'input_rejected') { inputEnabled = false; return; }
    if (message.t !== 'frame') return;
    const version = ++frameVersion;
    const image = new Image();
    image.onload = () => {
      if (disposed || version !== frameVersion) return;
      canvas.width = message.w;
      canvas.height = message.h;
      canvas.getContext('2d').drawImage(image, 0, 0);
    };
    image.src = 'data:image/jpeg;base64,' + message.data;
  };
  socket.onerror = () => { if (!disposed) onEvent('error'); };
  socket.onclose = () => {
    if (!disposed) { onEvent('disconnected'); dispose(); }
  };

  function mouse(event, type) {
    const box = canvas.getBoundingClientRect();
    return { t: 'mouse', type,
      x: (event.clientX - box.left) * canvas.width / box.width,
      y: (event.clientY - box.top) * canvas.height / box.height,
      button: ['left', 'middle', 'right'][event.button] || 'left' };
  }
  function listen(name, listener) {
    canvas.addEventListener(name, listener, { signal: controller.signal });
  }
  listen('click', (event) => { canvas.focus(); send(mouse(event, 'click')); });
  listen('wheel', (event) => {
    event.preventDefault();
    send({ ...mouse(event, 'wheel'), dx: event.deltaX, dy: event.deltaY });
  });
  listen('keydown', (event) => {
    event.preventDefault();
    if (event.isComposing) return;
    const key = event.key;
    send(key.length === 1 ? { t: 'text', text: key } : { t: 'key', type: 'press', key });
  });
  listen('compositionend', (event) => {
    if (event.data) send({ t: 'text', text: event.data });
  });
  return handle;
}
