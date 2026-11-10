// Кнопка «Скопировать» у блоков с кодом.
document.addEventListener('click', function (e) {
  var btn = e.target.closest && e.target.closest('button');
  if (!btn || btn.textContent.trim() !== 'Скопировать') return;
  var box = btn.closest('div');
  while (box && !box.querySelector('pre')) box = box.parentElement;
  var pre = box && box.querySelector('pre');
  if (!pre || !navigator.clipboard) return;
  navigator.clipboard.writeText(pre.innerText).then(function () {
    btn.textContent = 'Скопировано';
    setTimeout(function () { btn.textContent = 'Скопировать'; }, 1500);
  });
});
