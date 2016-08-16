function createAutoClosingAlert(selector, delay) {
   var alert = $(selector).alert();
   window.setTimeout(function() { alert.hide() }, delay);
}
