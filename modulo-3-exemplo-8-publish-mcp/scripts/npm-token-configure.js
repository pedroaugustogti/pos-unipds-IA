const buttons = [...document.querySelectorAll('button')];
const packageReadWrite = buttons.find((b, idx) => {
  const text = b.textContent.trim();
  if (text !== 'Read and write') return false;
  const section = b.closest('section, div');
  return section?.textContent?.includes('Packages and scopes');
}) ?? buttons.filter((b) => b.textContent.trim() === 'Read and write')[0];

packageReadWrite?.click();

const bypass = document.querySelector('input[type="checkbox"]');
if (bypass && !bypass.checked) bypass.click();

JSON.stringify({
  clicked: packageReadWrite?.textContent?.trim() ?? null,
  bypass2fa: bypass?.checked ?? null,
  summary: document.body.innerText.match(/This token will:[\s\S]*?Generate token/)?.[0] ?? '',
});
