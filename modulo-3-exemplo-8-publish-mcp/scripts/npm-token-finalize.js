(() => {
  const allPackages = document.getElementById('packagesAll');
  if (allPackages) {
    allPackages.click();
    allPackages.checked = true;
  }

  const buttons = [...document.querySelectorAll('button')].filter((b) => b.textContent.trim() === 'Read and write');
  if (buttons[0]) buttons[0].click();

  const bypass = document.getElementById('create-gat_bypass2FA');
  if (bypass && !bypass.checked) bypass.click();

  return JSON.stringify({
    allPackages: allPackages?.checked ?? null,
    bypass2fa: bypass?.checked ?? null,
    summary: document.body.innerText.match(/This token will:[\s\S]*?Generate token/)?.[0] ?? '',
  });
})();
