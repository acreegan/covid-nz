
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
    if (value == "tab_1"){
        setTimeout(allDescendantsAutocompleteOffWithId,3000,"dropdown_tab_1")
    }
    else if (value == "tab_2"){
        setTimeout(allDescendantsAutocompleteOffWithId,3000,"dropdown_tab_2")
    }
    else if (value == "tab_3"){
        setTimeout(allDescendantsAutocompleteOffWithId,3000,"dropdown_tab_3")
    }

    return null;
  }
};


// Run on load (need func so get element doesn't get evaluated until after timeout)
setTimeout(allDescendantsAutocompleteOffWithId,5000,"countries")




