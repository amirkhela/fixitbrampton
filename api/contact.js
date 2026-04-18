const { Resend } = require("resend");

const resend = new Resend(process.env.RESEND_API_KEY);

module.exports = async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const { name, phone, message } = req.body || {};

  if (!name || !phone || !message) {
    return res.status(400).json({ error: "All fields are required" });
  }

  try {
    await resend.emails.send({
      from: "Fix It Brampton <fixit@clawdmarketing.com>",
      to: "fixitbrampton@gmail.com",
      bcc: "amir.khela@gmail.com",
      reply_to: "fixitbrampton@gmail.com",
      subject: `New inquiry from ${name}`,
      text: [
        "New Fix It Brampton inquiry:",
        "",
        `Name: ${name}`,
        `Phone: ${phone}`,
        "",
        "Message:",
        message,
      ].join("\n"),
    });

    return res.status(200).json({ success: true });
  } catch (err) {
    console.error("Resend error:", err);
    return res.status(500).json({ error: "Failed to send email" });
  }
};
