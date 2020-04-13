
function allDescendantsAutocompleteOff (node) {
    for (var i = 0; i < node.childNodes.length; i++) {
      var child = node.childNodes[i];
      allDescendantsAutocompleteOff(child);
      if (child.nodeType==1){
        child.setAttribute("autocomplete","off")
      }
    }
}


function allDescendantsAutocompleteOffWithId(id)
{
    allDescendantsAutocompleteOff(document.getElementById(id))
}

if (!window.dash_clientside) {
  window.dash_clientside = {};
}
window.dash_clientside.clientside = {
  autocomplete_off: function(value) {
    if (value == "tab-1"){
        setTimeout(allDescendantsAutocompleteOffWithId,3000,"countries")
    }
    else{
        setTimeout(allDescendantsAutocompleteOffWithId,3000,"countries2")
    }

    return null;
  }
};


// Run on load (need func so get element doesn't get evaluated until after timeout)
setTimeout(allDescendantsAutocompleteOffWithId,5000,"countries")




