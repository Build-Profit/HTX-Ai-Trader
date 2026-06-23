export function drawEquityChart(canvas, points) {
  const context = canvas.getContext("2d");
  const pixelRatio = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  canvas.width = Math.max(1, Math.floor(rect.width * pixelRatio));
  canvas.height = Math.max(1, Math.floor(rect.height * pixelRatio));
  context.scale(pixelRatio, pixelRatio);

  const width = rect.width;
  const height = rect.height;
  context.clearRect(0, 0, width, height);
  paintBackground(context, width, height);

  if (!points || points.length < 2) {
    drawEmpty(context, width, height);
    return;
  }

  const values = points.map((point) => Number(point.equity));
  const min = Math.min(...values);
  const max = Math.max(...values);
  const spread = Math.max(1, max - min);
  const pad = {
    top: 24,
    right: 18,
    bottom: 34,
    left: 54,
  };
  const plotWidth = width - pad.left - pad.right;
  const plotHeight = height - pad.top - pad.bottom;

  drawGrid(context, pad, plotWidth, plotHeight, min, max);
  drawLine(context, points, min, spread, pad, plotWidth, plotHeight);
}

function paintBackground(context, width, height) {
  context.fillStyle = "#101214";
  context.fillRect(0, 0, width, height);
}

function drawEmpty(context, width, height) {
  context.fillStyle = "#9ca6a6";
  context.font = "13px system-ui, sans-serif";
  context.textAlign = "center";
  context.fillText("No equity data", width / 2, height / 2);
}

function drawGrid(context, pad, plotWidth, plotHeight, min, max) {
  context.strokeStyle = "#2f343a";
  context.lineWidth = 1;
  context.fillStyle = "#9ca6a6";
  context.font = "11px ui-monospace, monospace";
  context.textAlign = "right";

  for (let index = 0; index <= 4; index += 1) {
    const y = pad.top + (plotHeight / 4) * index;
    const value = max - ((max - min) / 4) * index;
    context.beginPath();
    context.moveTo(pad.left, y);
    context.lineTo(pad.left + plotWidth, y);
    context.stroke();
    context.fillText(value.toFixed(2), pad.left - 8, y + 4);
  }
}

function drawLine(context, points, min, spread, pad, plotWidth, plotHeight) {
  context.strokeStyle = "#3ddc84";
  context.lineWidth = 2;
  context.beginPath();

  points.forEach((point, index) => {
    const x = pad.left + (plotWidth / (points.length - 1)) * index;
    const y = pad.top + plotHeight - ((Number(point.equity) - min) / spread) * plotHeight;
    if (index === 0) {
      context.moveTo(x, y);
    } else {
      context.lineTo(x, y);
    }
  });
  context.stroke();

  const last = points[points.length - 1];
  const lastX = pad.left + plotWidth;
  const lastY = pad.top + plotHeight - ((Number(last.equity) - min) / spread) * plotHeight;
  context.fillStyle = "#3ddc84";
  context.beginPath();
  context.arc(lastX, lastY, 4, 0, Math.PI * 2);
  context.fill();
}
