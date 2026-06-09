const samples = [
  {
    source: "Hello.",
    target: "你好",
  },
  {
    source: "Thank you.",
    target: "谢谢",
  },
  {
    source: "Where is the train station?",
    target: "火车站在哪里？",
  },
  {
    source: "Where is the restroom?",
    target: "请问洗手间在哪里？",
  },
  {
    source: "I would like a cup of coffee.",
    target: "我想点一杯咖啡。",
  },
  {
    source: "The meeting is at three this afternoon.",
    target: "今天下午三点开会。",
  },
  {
    source: "Numbers",
    target: "1234567890",
  },
];

const captionEl = document.getElementById("caption");
const sourceEl = document.getElementById("source");
const statusEl = document.getElementById("status");
const clockEl = document.getElementById("clock");
const modeEl = document.getElementById("mode");

let sampleIndex = 2;
let fontSize = 46;
let paused = false;
let reconnectDelay = 500;
let socket = null;

function setStatus(text, state) {
  statusEl.textContent = text;
  statusEl.dataset.state = state || "";
}

function setMode(mode) {
  if (mode === "zh_to_en") {
    modeEl.textContent = "中文 -> EN";
    document.documentElement.lang = "en";
    return;
  }
  modeEl.textContent = "EN -> 中文";
  document.documentElement.lang = "zh-Hans";
}

function setCaption(target, source) {
  if (paused) {
    return;
  }
  captionEl.textContent = target || "";
  sourceEl.textContent = source || "";
  clockEl.textContent = new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function showSample(index) {
  const sample = samples[index];
  setCaption(sample.target, sample.source);
}

function changeFont(delta) {
  fontSize = Math.max(32, Math.min(68, fontSize + delta));
  document.documentElement.style.setProperty("--font-size", `${fontSize}px`);
}

function clearCaption() {
  captionEl.textContent = "";
  sourceEl.textContent = "";
}

function handleCaptionMessage(payload) {
  if (payload.type === "caption") {
    setMode(payload.mode);
    setCaption(payload.target_text, payload.source_text);
  }
  if (payload.type === "status") {
    setStatus(payload.status === "connected" ? "已连接" : payload.status, payload.status);
  }
}

function connectSocket() {
  if (!window.CAPTION_WS_URL) {
    setStatus("未配置", "disconnected");
    return;
  }

  socket = new WebSocket(window.CAPTION_WS_URL);
  setStatus("连接中", "connecting");

  socket.addEventListener("open", () => {
    reconnectDelay = 500;
    setStatus("已连接", "connected");
  });

  socket.addEventListener("message", (event) => {
    try {
      handleCaptionMessage(JSON.parse(event.data));
    } catch (_error) {
      setStatus("消息错误", "error");
    }
  });

  socket.addEventListener("close", () => {
    setStatus("未连接", "disconnected");
    const delay = reconnectDelay;
    reconnectDelay = Math.min(reconnectDelay * 1.8, 10000);
    window.setTimeout(connectSocket, delay);
  });

  socket.addEventListener("error", () => {
    setStatus("连接错误", "error");
    socket.close();
  });
}

document.addEventListener("keydown", (event) => {
  if (event.key === "ArrowRight") {
    sampleIndex = (sampleIndex + 1) % samples.length;
    showSample(sampleIndex);
  }
  if (event.key === "ArrowLeft") {
    sampleIndex = (sampleIndex - 1 + samples.length) % samples.length;
    showSample(sampleIndex);
  }
  if (event.key === "ArrowUp") {
    changeFont(4);
  }
  if (event.key === "ArrowDown") {
    changeFont(-4);
  }
  if (event.key === "Enter") {
    paused = !paused;
    setStatus(paused ? "已暂停" : "已连接", paused ? "paused" : "connected");
  }
  if (event.key === "Escape") {
    clearCaption();
  }
});

showSample(sampleIndex);
connectSocket();
