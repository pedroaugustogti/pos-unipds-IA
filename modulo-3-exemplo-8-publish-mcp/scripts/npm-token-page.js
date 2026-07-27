const sections = [...document.querySelectorAll('h2')].map((h) => ({
  heading: h.textContent.trim(),
  html: h.parentElement?.innerHTML?.slice(0, 500) ?? '',
}));

const radios = [...document.querySelectorAll('input[type="radio"]')].map((el, i) => ({
  i,
  name: el.name,
  value: el.value,
  id: el.id,
  checked: el.checked,
  label: el.labels?.[0]?.textContent?.trim() ?? '',
}));

const buttons = [...document.querySelectorAll('button')].map((el, i) => ({
  i,
  text: el.textContent.trim(),
}));

JSON.stringify({ sections: sections.map((s) => s.heading), radios, buttons }, null, 2);
