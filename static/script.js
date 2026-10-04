const menuBtn = document.querySelector('.menu-btn');
const navLinks = document.querySelector('.nav-links');
if (menuBtn) menuBtn.addEventListener('click', () => navLinks.classList.toggle('open'));

document.querySelectorAll('.nav-links a').forEach(a => a.addEventListener('click', () => navLinks?.classList.remove('open')));

document.querySelectorAll('[data-package]').forEach(link => {
  link.addEventListener('click', () => {
    const select = document.querySelector('select[name="package"]');
    if (select) select.value = link.dataset.package;
  });
});
