function Cancelar(nombre, email, cotizacion, cotizaciontotal,fecha){
    cotizacion = cotizacion.replace('\n','')
   Swal.fire({
        title: "Cotización para "+nombre,
        html: `
        <form action="/cotizacion" name="form_cotizacion" method="POST">
        <input type="hidden" name="nombre" value="`+nombre+`"><input type="hidden" name="fecha" value="`+fecha+`">
        Email: <input type="email" class="swal2-input" id="email" name="email" value=" `+email+`" required><br><br>
        <textarea name="cotizacion" id="cotizacion" cols="30" rows="15" style="font-size: 22px; text-transform: uppercase; width: 90%;" placeholder="Ingrese una cotización..." required>`+cotizacion+`</textarea><br>
        Total $:<input type="number" name="cotizaciontotal" id="cotizaciontotal" class="swal2-input" value="`+cotizaciontotal+`" required>
        </form>
        `,
        focusConfirm: false,
        preConfirm: () => {
            if(document.getElementById('email').value == '' || document.getElementById('email').value == ' ' || document.getElementById('cotizaciontotal').value == '' || document.getElementById('cotizaciontotal').value == ' '){
                ErrorAlert(document.getElementById('email').value);
            }else{
                document.form_cotizacion.submit();
                Success(document.getElementById('email').value); 
            }
        }
      });
};

function cotizacionListo(fecha){
    let opcion = confirm("El registro quedará guardado como Listo!");
    if (opcion == true) {
        document.getElementById('cotizacion_listo').value = fecha;
        document.form_cotizacion_listo.submit();
	}
}

function Success(correo){
    Swal.fire({
        title: "Cotización enviada!",
        text: "Se contactó a la dirección "+correo,
        icon: "success"
      });
}

function ErrorAlert(correo){
    Swal.fire({
        title: "Hubo un error!",
        text: "Revise la dirección de email ingresada: "+correo,
        icon: "error"
      });
}

function registroListo(msg){
    Swal.fire({
        title: "Listo!",
        text: msg,
        icon: "success"
      });
}

function clienteAgregado(){
    let opcion = confirm("¡Está registrando un nuevo cliente!");
    if (opcion == true) {
        Swal.fire({
            title: "Listo!",
            text: "Cliente nuevo registrado con éxito!",
            icon: "success"
          });
        document.ficha.submit()
        }
}

function borrarRegistro(pregunta, texto,id_submit){
    let opcion = confirm(pregunta);
    if (opcion == true) {
        Swal.fire({
            title: "Listo!",
            text: texto,
            icon: "info"
          });
        document.getElementById(id_submit).click();
	}
}

function usuarioAgregado(){
    let opcion = confirm('¡Está agregando un usuario nuevo!');
    if (opcion == true) {
        Swal.fire({
            title: "Listo!",
            text: "Usuario nuevo registrado con éxito!",
            icon: "success"
          });
        document.getElementById("submit_altausuario").click();
	}
}

function nuevaTarea(){
   Swal.fire({
        title: "Nueva tarea",
        html: `
        <form action="/tareas/altatarea" method="POST">
        <textarea name="tarea" cols="30" rows="15" style="font-size: 22px; text-transform: uppercase; width: 90%;" placeholder="Tarea nueva..." required></textarea>
        <button type="submit" id="btn-altatarea" hidden></button>
        </form>
        `,
        focusConfirm: false,
        preConfirm: () => {
            document.getElementById('btn-altatarea').click()
            registroListo('Tarea agregada con éxito!')
            }
      });
};

function modificarTarea(idtarea, tareavieja){
    Swal.fire({
         title: "Modificar tarea",
         html: `
         <form action="/tareas/editartarea" method="POST">
         <textarea name="tareanueva" cols="30" rows="15" style="font-size: 22px; text-transform: uppercase; width: 90%;" required>`+tareavieja+`</textarea>
         <input type="hidden" name="idtarea" value="`+idtarea+`"><input type="hidden" name="tareavieja" value="`+tareavieja+`">
         <button type="submit" id="btn-modtarea" hidden></button>
         </form>
         `,
         focusConfirm: false,
         preConfirm: () => {
            document.getElementById('btn-modtarea').click()
            registroListo('Tarea modificada con éxito!')
             }
       });
 };

 function nuevoPlan(){
    Swal.fire({
         title: "Nuevo plan",
         html: `
         <form action="/planes/nuevoplan" method="POST">
         <input type="text" style="text-transform: uppercase; margin: 0 auto;" class="swal2-input" name="plan" placeholder="Nombre del plan nuevo..."><br> 
         <textarea name="desc_plan" cols="30" rows="15" style="font-size: 22px; text-transform: uppercase; width: 90%; margin: 0 auto;" placeholder="Descripción..." required></textarea><br>
         Precio:<input type="number" class="swal2-input" name="precioplan" placeholder="$" style="width: 30%; margin: 0 auto;">
         <button type="submit" id="btn-altaplan" hidden></button>
         </form>
         `,
         focusConfirm: false,
         preConfirm: () => {
            document.getElementById('btn-altaplan').click()
            registroListo('Plan agregado con éxito!')
            }
       });
 };

 function modificarPlan(id, plan, desc, precio){
    Swal.fire({
         title: "Modificar plan",
         html: `
         <form action="/planes/editarplan" method="POST">
         <input type="hidden" name="idplan" value="`+id+`">
         <input type="text" style="text-transform: uppercase; margin: 0 auto;" class="swal2-input" name="plan" value="`+plan+`"><br> 
         <textarea name="desc_plan" cols="30" rows="15" style="font-size: 22px; text-transform: uppercase; width: 90%; margin: 0 auto;" required>`+desc+`</textarea><br>
         Precio:<input type="number" class="swal2-input" name="precioplan" value="`+precio+`" style="width: 30%; margin: 0 auto;">
         <button type="submit" id="btn-modplan" hidden></button>
         </form>
         `,
         focusConfirm: false,
         preConfirm: () => {
            document.getElementById('btn-modplan').click()
            registroListo('Plan modificado con éxito!')
            }
       });
 };