
function allDescendantsAutocompleteOff (node) {
    for (var i = 0; i < node.childNodes.length; i++) {
      var child = node.childNodes[i];
      allDescendantsAutocompleteOff(child);
      if (child.nodeType==1){
        child.setAttribute("autocomplete","off")
      }
    }
}


function func(node)
{
    allDescendantsAutocompleteOff(document.getElementById("countries"))
}


setTimeout(func,5000)




