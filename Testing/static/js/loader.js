(function () {
  const loader = document.getElementById('appLoader');
  const messageNode = loader ? loader.querySelector('#appLoaderMessage') : null;
  const defaultMessage = messageNode ? messageNode.textContent.trim() || 'Cargando…' : 'Cargando…';

  if (!loader) {
    window.Loader = {
      show() {},
      hide() {},
      wrap(task) {
        if (typeof task === 'function') {
          return Promise.resolve().then(task);
        }
        return Promise.resolve(task);
      },
      fetch(input, init) {
        return fetch(input, init);
      }
    };
    return;
  }

  let pending = 0;
  let hideTimeoutId = null;

  function normaliseOptions(messageOrOptions) {
    if (!messageOrOptions) return {};
    if (typeof messageOrOptions === 'string') {
      return { message: messageOrOptions };
    }
    return { ...messageOrOptions };
  }

  function setVisible(visible) {
    loader.classList.toggle('is-visible', visible);
    loader.setAttribute('aria-hidden', visible ? 'false' : 'true');
    document.body.classList.toggle('loader-lock', visible);
  }

  function setMessage(message) {
    if (!messageNode) return;
    if (typeof message === 'string' && message.trim().length > 0) {
      messageNode.textContent = message.trim();
    } else {
      messageNode.textContent = defaultMessage;
    }
  }

  function show(messageOrOptions) {
    const { message } = normaliseOptions(messageOrOptions);
    if (hideTimeoutId) {
      clearTimeout(hideTimeoutId);
      hideTimeoutId = null;
    }

    setMessage(message);
    if (pending === 0) {
      setVisible(true);
    }
    pending += 1;
  }

  function hide(messageOrOptions) {
    const { resetMessage = true } = normaliseOptions(messageOrOptions);
    pending = Math.max(0, pending - 1);
    if (pending > 0) return;

    hideTimeoutId = window.setTimeout(() => {
      setVisible(false);
      hideTimeoutId = null;
      if (resetMessage) {
        setMessage();
      }
    }, 120);
  }

  async function wrap(task, messageOrOptions) {
    const runner = typeof task === 'function' ? task : () => task;
    show(messageOrOptions);
    try {
      return await runner();
    } finally {
      hide(messageOrOptions);
    }
  }

  async function fetchWithLoader(input, init, messageOrOptions) {
    show(messageOrOptions);
    try {
      return await fetch(input, init);
    } finally {
      hide(messageOrOptions);
    }
  }

  window.Loader = {
    show,
    hide,
    wrap,
    fetch: fetchWithLoader
  };
}());
