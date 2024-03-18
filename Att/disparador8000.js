const { Client, LocalAuth, MessageMedia } = require("whatsapp-web.js");

const express = require("express");
const { body, validationResult } = require("express-validator");
const socketIO = require("socket.io");
const qrcode = require("qrcode");
const http = require("http");
const fileUpload = require("express-fileupload");
const axios = require("axios");
const mime = require("mime-types");
const port = process.env.PORT || 8000;
const app = express();
const server = http.createServer(app);
const io = socketIO(server);
const fs = require("fs");
const colors = require("colors");
const path = require("path");
const base_path = process.env._MEIPASS || __dirname;
const mysql = require("mysql");

app.use(express.json());
app.use(
  express.urlencoded({
    extended: true,
  })
);
app.use(
  fileUpload({
    debug: false,
  })
);
app.use("/", express.static(__dirname + "/"));

app.get("/", (req, res) => {
  res.sendFile("index.html", {
    root: __dirname,
  });
});

// Configuração do pool de conexão com o banco de dados
const pool = mysql.createPool({
  host: "login-database.cambz5iefybx.us-east-1.rds.amazonaws.com",
  user: "admin",
  password: "WFHzZoa#",
  database: "logins",
});

// Função para executar uma consulta SQL
async function executarConsulta() {
  return new Promise((resolve, reject) => {
    pool.getConnection((err, connection) => {
      if (err) {
        console.error("Erro ao conectar ao banco de dados:", err);
        return;
      }

      connection.query(
        "SELECT numeros FROM envios_e_status",
        (error, results, fields) => {
          connection.release();
          if (error) {
            console.error("Erro ao executar a consulta:", error);
            return;
          }
          resolve(results);
        }
      );
    });
  });
}

const client = new Client({
  authStrategy: new LocalAuth({ clientId: "bot-zdg5" }),
  puppeteer: {
    headless: true,
    args: [
      "--no-sandbox",
      "--disable-setuid-sandbox",
      "--disable-dev-shm-usage",
      "--disable-accelerated-2d-canvas",
      "--no-first-run",
      "--no-zygote",
      "--single-process", // <- this one doesn't works in Windows
      "--disable-gpu",
    ],
  },
});

client.initialize();

io.on("connection", function (socket) {
  socket.emit("message", "Iniciando disparador...");

  client.on("qr", (qr) => {
    console.log("QRCode recebido! Aponte a câmera do celular.".cyan);
    qrcode.toDataURL(qr, (err, url) => {
      socket.emit("qr", url);
      socket.emit("message", "QRCode recebido, aponte a câmera  seu celular!");
    });
  });

  client.on("ready", () => {
    console.log("Dispositivo pronto!".green);
    socket.emit("ready", "Dispositivo pronto!".green);
    socket.emit("message", "Dispositivo pronto!");
    socket.emit("qr", "check.svg");
  });

  client.on("authenticated", () => {
    socket.emit("authenticated", "Autenticado!");
    socket.emit("message", "Autenticado!");
  });

  client.on("auth_failure", function () {
    socket.emit("message", "Falha na autenticação, reiniciando...");
    console.error("Falha na autenticação!".red);
  });

  client.on("disconnected", (reason) => {
    socket.emit("message", "Cliente desconectado!");
    console.log("Cliente desconectado".red, reason);
    client.initialize();
  });
});

// Send message
app.post("/send-message", async (req, res) => {
  const errors = validationResult(req).formatWith(({ msg }) => {
    return msg;
  });

  if (!errors.isEmpty()) {
    return res.status(422).json({
      status: false,
      message: errors.mapped(),
    });
  }

  const number = req.body.number;
  const numberDDI = number.substr(0, 2);
  const numberDDD = number.substr(2, 2);
  let numberUser = number.substr(-9, 9);
  let numberUser2 = number.substr(-8, 8);
  const message = req.body.message;

  if (numberDDI !== "55") {
    const numberZDG = number + "@c.us";
    client
      .sendMessage(numberZDG, message)
      .then((response) => {
        res.status(200).json({
          status: true,
          message: "Mensagem enviada",
          response: response,
        });
      })
      .catch((err) => {
        res.status(500).json({
          status: false,
          message: "Mensagem não enviada",
          response: err.text,
        });
      });
  } else if (parseInt(numberDDD) >= 31 && numberUser.length > 8) {
    numberUser = numberUser.substring(1);
    const numberZDG = "55" + numberDDD + numberUser + "@c.us";
    client
      .sendMessage(numberZDG, message)
      .then((response) => {
        res.status(200).json({
          status: true,
          message: "Mensagem enviada",
          response: response,
        });
      })
      .catch((err) => {
        res.status(500).json({
          status: false,
          message: "Mensagem não enviada",
          response: err.text,
        });
      });
  } else if (parseInt(numberDDD) <= 31) {
    if (parseInt(numberUser2.charAt(0)) >= 6) {
      const numberZDG = "55" + numberDDD + "9" + numberUser2 + "@c.us";
      client
        .sendMessage(numberZDG, message)
        .then((response) => {
          res.status(200).json({
            status: true,
            message: "Mensagem enviada",
            response: response,
          });
        })
        .catch((err) => {
          res.status(500).json({
            status: false,
            message: "Mensagem não enviada",
            response: err.text,
          });
        });
    } else {
      const numberZDG = "55" + numberDDD + numberUser2 + "@c.us";
      client
        .sendMessage(numberZDG, message)
        .then((response) => {
          res.status(200).json({
            status: true,
            message: "Mensagem enviada",
            response: response,
          });
        })
        .catch((err) => {
          res.status(500).json({
            status: false,
            message: "Mensagem não enviada",
            response: err.text,
          });
        });
    }
  }
});

const numerosRedirecionados = {};
const numerosRedirecionados1 = {};
const numerosRedirecionados2 = {};

// Função para ler os dados do banco de dados MySQL
async function lerDadosDoBancoDeDados() {
  return new Promise((resolve, reject) => {
    pool.getConnection((err, connection) => {
      if (err) reject(err);

      const selectQuery = "SELECT * FROM configs_envios LIMIT 1";

      connection.query(selectQuery, (error, results, fields) => {
        connection.release();

        if (error) reject(error);

        resolve(results);
      });
    });
  });
}

async function lerDadosMensagemPersonalizada(contact) {
  try {
    const configData = await lerDadosDoBancoDeDados();

    let mensagemPersonalizada = configData[0].mensagemPersonalizada || "";

    const name = contact.pushname;
    mensagemPersonalizada = mensagemPersonalizada.replace("{{name}}", name);

    return mensagemPersonalizada;
  } catch (error) {
    console.error("Erro ao ler dados do JSON:", error);
    return ""; // Retorna uma string vazia em caso de erro
  }
}

async function inserirDadosDeLog(data, nome, numero, mensagem, numeroRedirecionado) {
  try {
    // Dividindo a data em componentes de data e hora
    const [dataParte, horaParte] = data.split(' ');

    // Convertendo a parte da data para o formato esperado pelo banco de dados
    const dataFormatada = dataParte.split('/').reverse().join('-');

    // Combinando a parte da data formatada com a parte da hora original
    const dataHoraFormatada = `${dataFormatada} ${horaParte}`;

    console.log(dataHoraFormatada);

    const insercaoQuery = `INSERT INTO logs_de_envio (data, nome, numero, mensagem, numeroRedirecionado) 
    VALUES (?, ?, ?, ?, ?)`;
    const valoresInsercao = [dataHoraFormatada, nome, numero, mensagem, numeroRedirecionado];

    // Execute a consulta de inserção
    await pool.query(insercaoQuery, valoresInsercao);

    console.log("Dados inseridos com sucesso!")
  } catch (error) {
    console.log("Erro ao inserir dados de log:", error)
  }
}

client.on("message", async (msg) => {
  const dadosBanco = await lerDadosDoBancoDeDados();
  const contact = await msg.getContact();
  const number = msg.from.split("@")[0];
  let numberUser = number.substring(-9, 9);

  if (
    msg.from.includes("@g.us") ||
    msg.from === "status@broadc" ||
    msg.from === "status@broadcast" ||
    msg.from === "@newsletter"
  ) {
    return;
  }

  if (!contact.isGroup) {
    const name = contact.pushname;
    const numerosFormatados = await executarConsulta();

    console.log("1:", numerosFormatados);
    console.log("2:", dadosBanco);
    console.log("3:", number);
    console.log("4:", numberUser);

    if (!number || !dadosBanco) {
      return;
    } else {
      const numberUserColored = number.green;
      console.log("\n");
      console.log("Número", numberUserColored, "válido no BD, da porta:", port);

      if (numerosRedirecionados1[number] || numerosRedirecionados2[number]) {
        return;
      }

      const msgGatilho1 = dadosBanco[0].msgGatilho1;
      const msgGatilho2 = dadosBanco[0].msgGatilho2;
      if (msg.body === msgGatilho1) {
        msg.react("🚀");
        const numberUserColored = number.green;
        const OneColored = String(msg.body).green;
        numerosRedirecionados1[number] = true;
        const currentDate = new Date();
        const dateTime = currentDate.toLocaleString("pt-BR", {
          timeZone: "America/Sao_Paulo",
        });

        const chat = await msg.getChat();
        chat.sendStateTyping();

        let labels = (await chat.getLabels()).map((l) => l.id);
        labels.push("0");
        labels.push("5");
        await chat.changeLabels(labels);

        const redirectNumber = dadosBanco[0].redirectNumber;
        const name = contact.pushname;

        // Adiciona a data e hora ao texto
        const textoComDataHora = `${dateTime}\nNome: ${name}\nNúmero: ${number}\nMensagem: ${msg.body}\nPorta: ${port}\n\n`;

        fs.appendFile("Gatilho 1.txt", textoComDataHora, (err) => {});

        function substituirOpcoes(match) {
          const opcoes = match.split("|");
          const opcaoAleatoria =
            opcoes[Math.floor(Math.random() * opcoes.length)];
          return opcaoAleatoria;
        }

        const textoGatilho1 = dadosBanco[0].textoGatilho1;

        // Substitui {{name}}
        const textoGatilho1ComNome = textoGatilho1.replace(/{{name}}/g, name);

        // Substitui opções dentro das chaves {}
        const textoGatilho1Substituido = textoGatilho1ComNome.replace(
          /\{(.*?)\}/g,
          (match, p1) => substituirOpcoes(p1)
        );

        setTimeout(() => {
          msg.reply(textoGatilho1Substituido);

          client.sendMessage(
            redirectNumber + "@c.us",
            `✅ *NOME:* ${name}\n✅ *NÚMERO:* ${number}\n✅ *MENSAGEM:* ${msg.body}\n✅ Entre em contato: https://wa.me/${numberUser}`
          );
          console.log(
            "Mensagem:",
            OneColored,
            "enviada para o número:",
            numberUserColored,
            "da porta:",
            port
          );
          console.log("\n");
        }, 15000); // 15 segundos em milissegundos
      } else if (msg.body === msgGatilho2) {
        msg.react("🚀");
        const numberUserColored = number.red;
        const TwoColored = String(msg.body).red;
        numerosRedirecionados2[number] = true;
        const currentDate = new Date();
        const dateTime = currentDate.toLocaleString("pt-BR", {
          timeZone: "America/Sao_Paulo",
        });
        const chat = await msg.getChat();
        chat.sendStateTyping();

        const redirectNumber = dadosBanco[0].redirectNumber;
        const name = contact.pushname;

        const textoComDataHora2 = `${dateTime}\nNome: ${name}\nNúmero: ${number}\nMensagem: ${msg.body}\nPorta: ${port}\n\n`;
        fs.appendFile("Gatilho 2.txt", textoComDataHora2, (err) => {});

        function substituirOpcoes(match) {
          const opcoes = match.split("|");
          const opcaoAleatoria =
            opcoes[Math.floor(Math.random() * opcoes.length)];
          return opcaoAleatoria;
        }

        const textoGatilho2 = dadosBanco[0].textoGatilho2;

        // Substitui {{name}}
        const textoGatilho2ComNome = textoGatilho2.replace(/{{name}}/g, name);

        // Substitui opções dentro das chaves {}
        const textoGatilho2Substituido = textoGatilho2ComNome.replace(
          /\{(.*?)\}/g,
          (match, p1) => substituirOpcoes(p1)
        );

        setTimeout(() => {
          msg.reply(textoGatilho2Substituido);
          client.sendMessage(
            redirectNumber + "@c.us",
            `⛔️ NOME: ${name}\n⛔️ NÚMERO: ${number}\n⛔️ MENSAGEM: ${msg.body}\n⛔️ Não tem interesse!`
          );
          console.log(
            "Mensagem:",
            TwoColored,
            "enviada para o número:",
            numberUserColored,
            "da porta:",
            port
          );
          console.log("\n");
        }, 10000); // 15 segundos em milissegundos
      }
    }

    if (msg.type === "chat" && typeof msg.body === "string") {
      // Verifique se o número já foi redirecionado antes de continuar
      if (numerosRedirecionados[number] || numerosRedirecionados2[number]) {
        return;
      }
      const msgGatilho1 = dadosBanco[0].msgGatilho1;
      const msgGatilho2 = dadosBanco[0].msgGatilho2;
      if (msg.body === msgGatilho1 || msg.body === msgGatilho2) {
        return;
      }

      if (!numerosRedirecionados[number]) {
        numerosRedirecionados[number] = true;
        // Verifica se é uma mensagem de chat

        // Obtém a data e hora atual
        const currentDate = new Date();
        const dateTime = currentDate.toLocaleString("pt-BR", {
          timeZone: "America/Sao_Paulo",
        });

        const redirectNumber = dadosBanco[0].redirectNumber;
        const chat = await msg.getChat();
        chat.sendStateTyping();

        await inserirDadosDeLog(dateTime, name, number, msg.body, redirectNumber);

        // Personaliza a mensagem usando os dados do JSON
        const mensagemPersonalizada = await lerDadosMensagemPersonalizada(contact);

        // Função para substituir as opções dentro das chaves {} por uma escolha aleatória
        function substituirOpcoes(match) {
          const opcoes = match.split("|");
          const opcaoAleatoria =
            opcoes[Math.floor(Math.random() * opcoes.length)];
          return opcaoAleatoria;
        }

        // Use uma expressão regular para encontrar as opções dentro das chaves {} e substituí-las aleatoriamente
        const mensagemPersonalizadaRandomizada = mensagemPersonalizada.replace(
          /{([^{}]+)}/g,
          (match, opcoes) => substituirOpcoes(opcoes)
        );

        const numberUserColored = number.green;

        // Adicione um timeout de 15 segundos antes de enviar a mensagem
        setTimeout(() => {
          msg.reply(mensagemPersonalizadaRandomizada);

          client.sendMessage(
            redirectNumber + "@c.us",
            `🖐🏻 *NOME:* ${name}\n🖐🏻 *NÚMERO:* ${number}\n🖐🏻 *MENSAGEM:* ${msg.body}\n🖐🏻 Entre em contato através do link: https://wa.me/${numberUser}`
          );
          console.log(
            "Segunda mensagem enviada para o número:",
            numberUserColored,
            "da porta:",
            port
          );
        }, 17000); // 15 segundos em milissegundos
      }
    }
  }
});

server.listen(port, function () {
  const portColored = String(port).yellow;
  console.log("Porta aberta:", portColored);
});
