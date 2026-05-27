import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

function nextFrame() {
  return new Promise((resolve) => requestAnimationFrame(() => resolve()));
}

async function waitForImagesInNode(node, { timeoutMs = 15000 } = {}) {
  const images = Array.from(node?.querySelectorAll?.('img') || []);
  if (images.length === 0) return;

  const perImagePromises = images.map((img) => {
    // If already loaded successfully, we're good.
    if (img.complete && img.naturalWidth > 0) {
      if (typeof img.decode === 'function') {
        return img.decode().catch(() => undefined);
      }
      return Promise.resolve();
    }

    // Otherwise wait for load/error (and try decode when available).
    return new Promise((resolve) => {
      const cleanup = () => {
        img.removeEventListener('load', onDone);
        img.removeEventListener('error', onDone);
      };
      const onDone = () => {
        cleanup();
        if (typeof img.decode === 'function') {
          img.decode().catch(() => undefined).finally(resolve);
        } else {
          resolve();
        }
      };

      img.addEventListener('load', onDone, { once: true });
      img.addEventListener('error', onDone, { once: true });
    });
  });

  // Global timeout to avoid hanging forever on a broken image.
  await Promise.race([
    Promise.all(perImagePromises),
    new Promise((resolve) => setTimeout(resolve, timeoutMs)),
  ]);
}

async function waitForFonts() {
  try {
    if (document?.fonts?.ready) {
      await document.fonts.ready;
    }
  } catch {
    // ignore
  }
}

export function createA4Pdf({ orientation = 'p' } = {}) {
  return new jsPDF({ orientation, unit: 'mm', format: 'a4' });
}

export function appendCanvasToA4Pdf(pdf, canvas, { marginMm = 10 } = {}) {
  const pageWidthMm = pdf.internal.pageSize.getWidth();
  const pageHeightMm = pdf.internal.pageSize.getHeight();
  const contentWidthMm = pageWidthMm - marginMm * 2;
  const contentHeightMm = pageHeightMm - marginMm * 2;

  const pxPerMm = canvas.width / contentWidthMm;
  const pageSliceHeightPx = Math.floor(contentHeightMm * pxPerMm);

  let renderedHeightPx = 0;
  let pageIndex = 0;

  while (renderedHeightPx < canvas.height) {
    const sliceHeightPx = Math.min(pageSliceHeightPx, canvas.height - renderedHeightPx);

    const pageCanvas = document.createElement('canvas');
    pageCanvas.width = canvas.width;
    pageCanvas.height = sliceHeightPx;

    const ctx = pageCanvas.getContext('2d');
    if (!ctx) throw new Error('Failed to create canvas context');

    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, pageCanvas.width, pageCanvas.height);

    ctx.drawImage(
      canvas,
      0,
      renderedHeightPx,
      canvas.width,
      sliceHeightPx,
      0,
      0,
      canvas.width,
      sliceHeightPx
    );

    // JPEG is significantly smaller than PNG and avoids memory spikes
    const imgData = pageCanvas.toDataURL('image/jpeg', 0.92);
    const imgHeightMm = sliceHeightPx / pxPerMm;

    if (pageIndex > 0) pdf.addPage();
    pdf.addImage(imgData, 'JPEG', marginMm, marginMm, contentWidthMm, imgHeightMm, undefined, 'FAST');

    renderedHeightPx += sliceHeightPx;
    pageIndex += 1;
  }
}

export function addCanvasAsFullPage(pdf, canvas) {
  const pageWidthMm = pdf.internal.pageSize.getWidth();
  const pageHeightMm = pdf.internal.pageSize.getHeight();

  const imgData = canvas.toDataURL('image/jpeg', 0.92);

  // Fit entire canvas onto a single page (contain)
  const imgAspect = canvas.width / canvas.height;
  const pageAspect = pageWidthMm / pageHeightMm;

  let drawW = pageWidthMm;
  let drawH = pageHeightMm;
  let x = 0;
  let y = 0;

  if (imgAspect > pageAspect) {
    // image is wider
    drawH = drawW / imgAspect;
    y = (pageHeightMm - drawH) / 2;
  } else {
    // image is taller
    drawW = drawH * imgAspect;
    x = (pageWidthMm - drawW) / 2;
  }

  pdf.addImage(imgData, 'JPEG', x, y, drawW, drawH, undefined, 'FAST');
}

export async function renderNodeToCanvas(node, { scale = 2 } = {}) {
  if (!node) throw new Error('Missing export node');
  await nextFrame();
  await nextFrame();

  const width = Math.max(node.scrollWidth || 0, node.offsetWidth || 0, node.clientWidth || 0);
  const height = Math.max(node.scrollHeight || 0, node.offsetHeight || 0, node.clientHeight || 0);
  if (!width || !height) {
    throw new Error('Export content has no size.');
  }

  return html2canvas(node, {
    scale,
    useCORS: true,
    backgroundColor: '#ffffff',
    logging: false,
    windowWidth: width,
    windowHeight: height,
    width,
    height,
  });
}

export async function exportNodeToPdfChunked({
  node,
  filename = 'student-report.pdf',
  marginMm = 10,
  scale = 2,
  chunkHeightPx = 12000,
} = {}) {
  if (!node) throw new Error('Missing export node');

  // Layout settle
  await nextFrame();
  await nextFrame();
  await waitForFonts();
  await waitForImagesInNode(node);

  const totalHeightPx = Math.max(node.scrollHeight, node.offsetHeight, 0);
  const totalWidthPx = Math.max(node.scrollWidth, node.offsetWidth, 0);
  if (!totalHeightPx || !totalWidthPx) throw new Error('Export content has no size.');

  const pdf = createA4Pdf();
  let firstChunk = true;

  for (let y = 0; y < totalHeightPx; y += chunkHeightPx) {
    const height = Math.min(chunkHeightPx, totalHeightPx - y);

    // Render only a window/crop of the node to avoid max canvas height limits.
    // html2canvas supports x/y/width/height cropping in CSS pixels.
    // eslint-disable-next-line no-await-in-loop
    const canvas = await html2canvas(node, {
      scale,
      useCORS: true,
      backgroundColor: '#ffffff',
      logging: false,
      windowWidth: totalWidthPx,
      windowHeight: height,
      x: 0,
      y,
      width: totalWidthPx,
      height,
      scrollX: 0,
      scrollY: 0,
    });

    if (!firstChunk) pdf.addPage();
    appendCanvasToA4Pdf(pdf, canvas, { marginMm });
    firstChunk = false;
  }

  pdf.save(filename);
}

export async function appendNodeToPdf({
  pdf,
  node,
  marginMm = 10,
  scale = 2,
} = {}) {
  if (!pdf) throw new Error('Missing pdf');
  if (!node) throw new Error('Missing export node');
  await waitForFonts();
  await waitForImagesInNode(node);
  const canvas = await renderNodeToCanvas(node, { scale });
  appendCanvasToA4Pdf(pdf, canvas, { marginMm });
}

export async function appendNodeToPdfChunked({
  pdf,
  node,
  marginMm = 10,
  scale = 2,
  chunkHeightPx = 12000,
} = {}) {
  if (!pdf) throw new Error('Missing pdf');
  if (!node) throw new Error('Missing export node');

  await waitForFonts();
  await waitForImagesInNode(node);

  const totalHeightPx = Math.max(node.scrollHeight, node.offsetHeight, 0);
  const totalWidthPx = Math.max(node.scrollWidth, node.offsetWidth, 0);
  if (!totalHeightPx || !totalWidthPx) throw new Error('Export content has no size.');

  for (let y = 0; y < totalHeightPx; y += chunkHeightPx) {
    const height = Math.min(chunkHeightPx, totalHeightPx - y);

    // eslint-disable-next-line no-await-in-loop
    const canvas = await html2canvas(node, {
      scale,
      useCORS: true,
      backgroundColor: '#ffffff',
      logging: false,
      windowWidth: totalWidthPx,
      windowHeight: height,
      x: 0,
      y,
      width: totalWidthPx,
      height,
      scrollX: 0,
      scrollY: 0,
    });

    appendCanvasToA4Pdf(pdf, canvas, { marginMm });

    // If there is remaining content, start the next chunk on a fresh page.
    if (y + chunkHeightPx < totalHeightPx) {
      pdf.addPage();
    }
  }
}

function getRelativeTop(el, root) {
  const r = root.getBoundingClientRect();
  const e = el.getBoundingClientRect();
  return e.top - r.top;
}

function computeSafeBreaksPx(root, selectors) {
  const els = selectors.flatMap((sel) => Array.from(root.querySelectorAll(sel)));
  const breaks = new Set();
  for (const el of els) {
    const top = getRelativeTop(el, root) + root.scrollTop;
    const bottom = top + el.getBoundingClientRect().height;
    // Add both start and end positions as potential breakpoints.
    // This allows us to "start a block on the next page" to avoid cutting it.
    if (Number.isFinite(top)) breaks.add(Math.max(0, Math.floor(top)));
    if (Number.isFinite(bottom)) breaks.add(Math.max(0, Math.floor(bottom)));
  }
  return Array.from(breaks).sort((a, b) => a - b);
}

function findSpanningBlockStart({ root, selectors, y, pageEnd }) {
  // If any "avoid" element spans across the intended page end,
  // return its top so we can push it to the next page.
  const els = selectors.flatMap((sel) => Array.from(root.querySelectorAll(sel)));
  let candidateTop = null;

  for (const el of els) {
    const top = getRelativeTop(el, root) + root.scrollTop;
    const height = el.getBoundingClientRect().height;
    const bottom = top + height;

    if (!Number.isFinite(top) || !Number.isFinite(bottom)) continue;
    // Only consider blocks that are within the current page window.
    if (top <= y + 1) continue;
    if (top < pageEnd && bottom > pageEnd) {
      // This element would be cut. Push it to next page by breaking at its start.
      if (candidateTop == null || top < candidateTop) {
        candidateTop = Math.floor(top);
      }
    }
  }

  return candidateTop;
}

function pickNextBreak({ y, targetBreak, safeBreaks, minFill }) {
  // Prefer the largest safeBreak <= targetBreak, but not too close to y (avoid tiny pages)
  let chosen = null;
  for (let i = safeBreaks.length - 1; i >= 0; i -= 1) {
    const b = safeBreaks[i];
    if (b <= y + 1) continue;
    if (b > targetBreak) continue;
    if (b - y < minFill) continue;
    chosen = b;
    break;
  }
  return chosen ?? targetBreak;
}

export async function appendNodeToPdfPaged({
  pdf,
  node,
  marginMm = 10,
  scale = 1.5,
  // elements that should not be cut between pages
  avoidSelectors = [
    '.insight-card',
    '.swot-card',
    '.sdp-semester-card',
    '.sdp-marksheet-item',
    '.sdp-form-card',
    '.sdp-forms-grid',
    '.sdp-meeting-card',
    '.sdp-attendance-card',
    '.sdp-activity-stat-card',
    '.sdp-activity-stats',
    '.sdp-support-stat-card',
    '.sdp-support-stats',
    '.sdp-exp-card',
    '.sdp-chain-card',
    '.sdp-timeline-item',
    '.sdp-section',
  ],
} = {}) {
  if (!pdf) throw new Error('Missing pdf');
  if (!node) throw new Error('Missing export node');

  await waitForFonts();
  await waitForImagesInNode(node);
  await nextFrame();
  await nextFrame();

  const pageWidthMm = pdf.internal.pageSize.getWidth();
  const pageHeightMm = pdf.internal.pageSize.getHeight();
  const contentWidthMm = pageWidthMm - marginMm * 2;
  const contentHeightMm = pageHeightMm - marginMm * 2;

  const totalHeightPx = Math.max(node.scrollHeight, node.offsetHeight, 0);
  const totalWidthPx = Math.max(node.scrollWidth, node.offsetWidth, 0);
  if (!totalHeightPx || !totalWidthPx) throw new Error('Export content has no size.');

  const pxPerMm = totalWidthPx / contentWidthMm;
  const pageHeightPx = Math.floor(contentHeightMm * pxPerMm);

  const safeBreaks = computeSafeBreaksPx(node, avoidSelectors);

  let y = 0;
  while (y < totalHeightPx) {
    const targetBreak = Math.min(y + pageHeightPx, totalHeightPx);
    // If a large card/table would be cut, start it on the next page even if it leaves whitespace.
    const spanningTop = findSpanningBlockStart({ root: node, selectors: avoidSelectors, y, pageEnd: targetBreak });

    // Try to fill the page reasonably, but prioritize not cutting blocks.
    const minFill = Math.floor(pageHeightPx * 0.25);
    let nextBreak = pickNextBreak({ y, targetBreak, safeBreaks, minFill });

    if (spanningTop != null && spanningTop > y + 1 && spanningTop < nextBreak) {
      // Break before the spanning block starts.
      nextBreak = spanningTop;
    }

    // Avoid pathological tiny pages (but still allow some whitespace when needed).
    if (nextBreak - y < Math.floor(pageHeightPx * 0.12) && targetBreak < totalHeightPx) {
      nextBreak = targetBreak;
    }
    const height = Math.max(1, nextBreak - y);

    // eslint-disable-next-line no-await-in-loop
    const canvas = await html2canvas(node, {
      scale,
      useCORS: true,
      backgroundColor: '#ffffff',
      logging: false,
      windowWidth: totalWidthPx,
      windowHeight: height,
      x: 0,
      y,
      width: totalWidthPx,
      height,
      scrollX: 0,
      scrollY: 0,
    });

    const imgData = canvas.toDataURL('image/jpeg', 0.92);
    const imgHeightMm = height / pxPerMm;
    pdf.addImage(imgData, 'JPEG', marginMm, marginMm, contentWidthMm, imgHeightMm, undefined, 'FAST');

    y = nextBreak;
    if (y < totalHeightPx) pdf.addPage();
  }
}

/**
 * Export a DOM node to a multi-page A4 PDF (portrait).
 * - Renders the node via html2canvas
 * - Slices the resulting canvas into page-sized chunks
 */
export async function exportNodeToPdf({
  node,
  filename = 'student-report.pdf',
  marginMm = 10,
  scale = 2,
} = {}) {
  const canvas = await renderNodeToCanvas(node, { scale });
  const pdf = createA4Pdf();
  appendCanvasToA4Pdf(pdf, canvas, { marginMm });
  pdf.save(filename);
}

