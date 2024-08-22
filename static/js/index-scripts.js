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
function onlyTwo(checkbox) {
  var checkboxes2 = document.getElementsByName('check2')
  checkboxes2.forEach((item) => {
      if (item !== checkbox) item.checked = false
  })
}

function btnCliente(telefono, email, cotizacion, total){
  alert("Teléfono: "+telefono+"\nEmail: "+email+"\nCotización: "+cotizacion+"\nCotización total: $"+total)
}

function btnCotizacion (cotizacion, total){
  alert("Cotización: "+cotizacion+"\nCotización total: $"+total)
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
/*
function editarCliente(campo, id, viejo, form, nombre){
  document.getElementById("eliminar").value = id;
  document.getElementById("nota").value = viejo
  document.getElementById("accion").value = campo;
  document.getElementById("cliente").value = nombre;

  let respuesta = prompt("Nuevo "+campo+":",viejo);
  if (respuesta != null){
      document.getElementById('agentenuevo').value = respuesta;
      document.getElementById(form).action = '/registros/editarregistro/actualizar';
      document.getElementById(form).submit()
  }
}

function editarSelect(accion, id, nuevo, viejo, nombre, form){
  document.getElementById("eliminar").value = id;
  document.getElementById("accion").value = accion;
  document.getElementById("agentenuevo").value = nuevo;
  document.getElementById("nota").value = viejo;
  document.getElementById("cliente").value = nombre;
  document.getElementById(form).submit();
}
*/
function comprobarEnTabla(idtabla, idinput, idlabel){
  let telefono = document.getElementById(idinput).value;
  let tablaTelefonos = document.getElementById(idtabla).getElementsByTagName('td');
  let notification = document.getElementById(idlabel);

  let encontrado = false;

  telefono = telefono.replace(/\D/g,'');

  for (let i=0; i< tablaTelefonos.length; i++){
    if (tablaTelefonos[i].textContent.trim() === telefono){
      encontrado = true;
      break;
    }
  }
  if (encontrado){
    notification.removeAttribute('hidden')
  }else{
    notification.setAttribute('hidden', 'hidden')
  }
  }

  document.addEventListener('DOMContentLoaded', function(){
   var appointmentInput = document.getElementsByName('appointment');
  flatpickr(appointmentInput, {
    enableTime: true,
    dateFormat: "Y-m-d H:i",
    time_24hr: true
  });
});

function cambiarRegistroPopUp(letra, idfecha, accion, nombre, telefono, datoviejo, redireccion, omitir){
  let datonuevo = prompt("Nuev"+letra+" "+accion, datoviejo);
  if (datonuevo != null){
    if (omitir){
      cambiarRegistro(datonuevo, idfecha, accion, nombre, telefono, redireccion, true);
    }else{
      cambiarRegistro(datonuevo, idfecha, accion, nombre, telefono, redireccion);
    }
  }
}

function cambiarRegistro(datonuevo, idfecha, accion, nombre, telefono, redireccion, omitir){
  if(!omitir){
    guardarFiltros();
  }
  var formData = {
      'datonuevo': datonuevo,
      'idfecha': idfecha,
      'accion': accion,
      'nombre': nombre,
      'telefono': telefono,
      'redireccion': redireccion
  };
  $.ajax({
      type: 'POST',
      url: '/registros/editarregistro/actualizar',
      data: formData,
      dataType: 'json',
      encode: true
  })
  .done(function(data){
      if(data.status === 'success'){
        if(data.redireccion){
          window.location.href = data.redireccion;
        }else{
          location.reload();
        }
      }else{
          alert('Error al modificar registro.')
      }
  })

  .fail(function(error) {
    alert("Error en la solicitud.");
    console.error('Error: ', error);
  });
}

function setearPopUp(idregistro, nombre, nota, tarea, fecha, hora, telefono, omitir){
  document.getElementById('m_id').value = idregistro;
  document.getElementById('m_cliente').innerHTML = nombre;
  document.getElementById('m_nombre').value = nombre;
  document.getElementById('m_notas').value = nota;
  document.getElementById('m_tareas').value = tarea;
  document.getElementById('m_telefono').value = telefono;
  //var appointmentInput = document.querySelector("input[name='appointment']");
  var appointmentInput = document.getElementById('calendario-emergente');
  var fp = flatpickr(appointmentInput, {enableTime: true, dateFormat: "Y-m-d H:i", time_24hr: true});
  fp.setDate(fecha+' '+hora, true, 'Y-m-d H:i');
  if(omitir){
    document.getElementById('boton-guardar-popup').addEventListener('click', function() {
      cambiarRegistro(document.getElementById('m_notas').value, document.getElementById('m_id').value, document.getElementById('calendario-emergente').value, document.getElementById('m_nombre').value, document.getElementById('m_telefono').value, document.getElementById('m_tareas').value, true)
    })
  }
  document.getElementById('myModal').style.display = 'flex';
}

function registrarPago(pago_condicional, empresa, motivo, idhoja, nombre, telefono, fecha_vencimiento, fecha_pago, forma_pago, pago, idrecordatorio){
  var formData = {
    'pago_condicional': pago_condicional,
    'empresa': empresa,
    'motivo': motivo,
    'idhoja': idhoja,
    'nombre': nombre,
    'telefono': telefono,
    'fecha_vencimiento': fecha_vencimiento,
    'fecha_pago': fecha_pago,
    'forma_pago': forma_pago,
    'pago': pago,
    'idrecordatorio': idrecordatorio
};
$.ajax({
    type: 'POST',
    url: '/pagos/registrarpago',
    data: formData,
    dataType: 'json',
    encode: true
})
.done(function(data){
    if(data.status === 'success'){
        registroListo('Pago registrado con éxito!')
        location.reload();
    }else{
        alert('Error al modificar registro.')
    }
})

.fail(function(error) {
  alert("Error en la solicitud.");
  console.error('Error: ', error);
});
}

function nuevoRegistro(url, nuevo){
  var formData = {
    'nuevo': nuevo
};
$.ajax({
    type: 'POST',
    url: url,
    data: formData,
    dataType: 'json',
    encode: true
})
.done(function(data){
    if(data.status === 'success'){
        location.replace('/empresas/'+data.redireccion)
    }else{
        alert('Error al guardar registro.')
    }
})

.fail(function(error) {
  alert("Error en la solicitud. Ha ingresado caracteres incorrectos o raros.");
  console.error('Error: ', error);
});
}