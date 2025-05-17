const http = require("http");
const { exec } = require("child_process");

http
  .createServer((req, res) => {
    if (req.method === "POST") {
      exec("cd ~/stockaffirm-agent && git pull && pm2 restart stockaffirm", (err, stdout, stderr) => {
        console.log(stdout || stderr);
      });
    }
    res.end("Webhook received");
  })
  .listen(9000, () => {
    console.log("🚀 Webhook server listening on port 9000");
  });
