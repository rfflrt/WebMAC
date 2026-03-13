async function enviarUsuario(){
    const dados = {
        nome: document.getElementById('nome').value,
        senha: document.getElementById('senha').value,
        bio: document.getElementById('bio').value
    };

    const resposta = await fetch('usuarios', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dados)
    });

    if(resposta.ok){
        const resultado = await resposta.json();
        alert("Usuário " + resultado.usuario + " criado!")
    }
    else{
        alert("Erro ao enviar!")
    }
}

async function pegarUsuario(){
    const dados = {
        nome: document.getElementById('nome').value,
        senha: document.getElementById('senha').value,
        bio: "momo"
    };

    const resposta = await fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dados)
    });

    if(resposta.ok){
        const msg = await resposta.json();
        alert(msg.message)
        window.location.href = '/home'
    }

    else{
        alert("Usuário não encontrado")
    }

}