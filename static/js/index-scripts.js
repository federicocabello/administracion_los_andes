function toggleSidebar(tamanio) {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');
    const footer = document.getElementById('footer');

    if (sidebar.style.left === tamanio) {
      sidebar.style.left = '0';
      mainContent.style.marginLeft = '250px';
      footer.style.marginLeft = '250px';
    }else{
      sidebar.style.left = '-250px';
      mainContent.style.marginLeft = '0';
      footer.style.marginLeft = '0';
    };
  }

  function onlyOne(checkbox) {
    var checkboxes = document.getElementsByName('check')
    checkboxes.forEach((item) => {
        if (item !== checkbox) item.checked = false
    })
}

function btnCliente(telefono, email, cotizacion, total){
  alert("Teléfono: "+telefono+"\nEmail: "+email+"\nCotización: "+cotizacion+"\nCotización total: $"+total)
}

function filtro(filtro, tabla, columna, cabeza) {
  // Declare variables
  var input, filter, table, tr, td, i, txtValue;
  input = document.getElementById(filtro);
  filter = input.value.toUpperCase();
  table = document.getElementById(tabla);
  tr = table.getElementsByTagName("tr");

  // Loop through all table rows, and hide those who don't match the search query
  for (i = cabeza; i < tr.length; i++) {
    td = tr[i].getElementsByTagName("td")[columna];
    if (td) {
      txtValue = td.textContent || td.innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    }
  }
}

function foco2(id){
  if( event.keyCode == 13){
    event.preventDefault();
    document.getElementById(id).focus();
  }
  }

function foco(id){
  if( event.keyCode == 13){
    document.getElementById(id).focus();
  }
}

function habilitarBoton(input, boton){
  if (document.getElementById(input).value.length > 0 && document.getElementById(input).value != ' '){
      document.getElementById(boton).removeAttribute('hidden')
  }else{
      document.getElementById(boton).setAttribute('hidden', 'hidden')
  }
}