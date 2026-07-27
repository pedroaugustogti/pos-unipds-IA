(() => {
  const all = [...document.querySelectorAll('button')];
  const rw = all.filter((b) => b.textContent.trim() === 'Read and write');
  if (rw[0]) rw[0].click();
  return JSON.stringify({ totalReadWrite: rw.length, summary: document.body.innerText.includes('read and write access to all packages') });
})();
