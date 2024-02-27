
function agregarArticulo(){
  let n = parseInt(document.ficha.n_articulos.value)+1;
  document.getElementById('art'+n).placeholder = "Artículo "+n+"";
  document.getElementById('art'+n).type = "text";
  document.getElementById('precio'+n).type = "number";
  document.getElementById('imagen'+n).type = "file";
  document.getElementById('art_descripcion'+n).removeAttribute("style");
  document.ficha.n_articulos.value = n;
  document.getElementById('art'+n).focus()
}

function eliminarArticulo(){
  let n = parseInt(document.ficha.n_articulos.value);
  document.getElementById('art'+n).type = "hidden";
  document.getElementById('art'+n).value = "";
  document.getElementById('precio'+n).type = "hidden";
  document.getElementById('precio'+n).value = "";
  document.getElementById('imagen'+n).type="hidden";
  document.getElementById('imagen'+n).value = null;
  document.getElementById('art_descripcion'+n).value = "";
  document.getElementById('art_descripcion'+n).style = "display: None;";
  document.ficha.n_articulos.value = n-1;
}

function agregarEspacio(){
  let n = parseInt(document.ficha.n_espacios.value)+1;
  document.getElementById('speech'+n).type = "text";
  document.getElementById('desc'+n).removeAttribute("style");
  cargarNEspacios();
  document.getElementById('speech'+n).focus()
}

function eliminarEspacio(){
  let n = parseInt(document.ficha.n_espacios.value);
  document.getElementById('speech'+n).type = "hidden";
  document.getElementById('speech'+n).value = "";
  document.getElementById('desc'+n).value = "";
  document.getElementById('desc'+n).style = "display: None;"
  cargarNEspacios();
}
function agregarPregunta(){
  let n = parseInt(document.ficha.n_preguntas.value)+1;
  document.getElementById('pregunta'+n).type = "text";
  document.getElementById('pregunta'+n).placeholder = "PREGUNTA N°"+n;
  cargarNPreguntas();
  document.getElementById('pregunta'+n).focus()
}

function eliminarPregunta(){
  let n = parseInt(document.ficha.n_preguntas.value);
  document.getElementById('pregunta'+n).type = "hidden";
  document.getElementById('pregunta'+n).value = "";
  cargarNPreguntas();
}

function cargarNArticulos(){
  const column1 = document.getElementById('column1');
  const inputs = column1.querySelectorAll('input');
  let visibles = 0;
  let ocultos = 0;
  inputs.forEach(function (input) {
    if(window.getComputedStyle(input).display !== 'none'){
      visibles++;
    } else {
      ocultos++;
    }
    });
    document.ficha.n_articulos.value = visibles/3;
}

function cargarNEspacios(){
  const column2 = document.getElementById('column2');
  const inputs = column2.querySelectorAll('input');
  let visibles = 0;
  let ocultos = 0;
  inputs.forEach(function (input) {
    if(window.getComputedStyle(input).display !== 'none'){
      visibles++;
    } else {
      ocultos++;
    }
    });
    document.ficha.n_espacios.value = visibles;
}

function cargarNPreguntas(){
  const column3 = document.getElementById('column3');
  const inputs = column3.querySelectorAll('input');
  let visibles = 0;
  let ocultos = 0;
  inputs.forEach(function (input) {
    if(window.getComputedStyle(input).display !== 'none'){
      visibles++;
    } else {
      ocultos++;
    }
    });
    document.ficha.n_preguntas.value = visibles;
}

function cargarContadores(){
  cargarNArticulos();
  cargarNEspacios();
  cargarNPreguntas();
}

function editarSpeech(sp_sp, sp_desc){
  let n = parseInt(document.ficha.n_espacios.value)+1;
  document.getElementById('speech'+n).type = "text";
  document.getElementById('desc'+n).removeAttribute("style");
  cargarNEspacios();
  document.getElementById('speech'+n).value = sp_sp;
  document.getElementById('desc'+n).value = document.getElementById(sp_desc).value;
  document.getElementById('desc'+n).focus();
}

function editarArticulo(art_art, art_precio, art_desc){
  let n = parseInt(document.ficha.n_articulos.value)+1;
  document.getElementById('art'+n).placeholder = "Artículo "+n+"";
  document.getElementById('art'+n).type = "text";
  document.getElementById('art'+n).value = art_art;
  document.getElementById('precio'+n).type = "number";
  document.getElementById('precio'+n).value = art_precio;
  document.getElementById('imagen'+n).type = "file";
  document.getElementById('art_descripcion'+n).removeAttribute("style");
  document.getElementById('art_descripcion'+n).value = document.getElementById(art_desc).value;
  document.ficha.n_articulos.value = n;
  document.getElementById('art'+n).focus();
}

function editarPregunta(pg_pg){
  let n = parseInt(document.ficha.n_preguntas.value)+1;
  document.getElementById('pregunta'+n).type = "text";
  document.getElementById('pregunta'+n).value = pg_pg;
  cargarNPreguntas();
  document.getElementById('pregunta'+n).focus()
}