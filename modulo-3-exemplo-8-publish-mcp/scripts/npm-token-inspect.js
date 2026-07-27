(() => {
  const inputs = [...document.querySelectorAll('input, select, [role=combobox], [role=listbox], [role=option]')].map((el) => ({
    tag: el.tagName,
    type: el.getAttribute('type'),
    role: el.getAttribute('role'),
    placeholder: el.getAttribute('placeholder'),
    name: el.getAttribute('name'),
    id: el.id,
    text: (el.textContent || '').trim().slice(0, 100),
    value: el.value,
  }));
  const clickable = [...document.querySelectorAll('button, a, label, [role=button]')]
    .map((el) => (el.textContent || '').trim())
    .filter((t) => /scope|package|gorgan|select|add|all/i.test(t))
    .slice(0, 40);
  return JSON.stringify({ inputs, clickable }, null, 2);
})();
