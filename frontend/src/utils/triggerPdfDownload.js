/**
 * Save a PDF Blob to the browser Downloads folder.
 * Important: do NOT set target="_blank" on the anchor — Chrome then opens the PDF
 * in a new tab instead of using the download bar / Downloads folder.
 */
export function triggerPdfDownload(blob, filename) {
  if (!blob || blob.size === 0) {
    throw new Error('Empty PDF data');
  }
  const pdfBlob =
    blob.type && blob.type.includes('pdf')
      ? blob
      : new Blob([blob], { type: 'application/pdf' });

  const objectUrl = URL.createObjectURL(pdfBlob);
  const a = document.createElement('a');
  a.href = objectUrl;
  a.download = filename || 'document.pdf';
  a.style.display = 'none';
  document.body.appendChild(a);
  a.click();

  requestAnimationFrame(() => {
    setTimeout(() => {
      try {
        if (a.parentNode) document.body.removeChild(a);
        URL.revokeObjectURL(objectUrl);
      } catch (_) {
        /* ignore */
      }
    }, 3000);
  });
}
