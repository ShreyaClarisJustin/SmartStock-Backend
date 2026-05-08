# const nodemailer = require("nodemailer");

# const transporter = nodemailer.createTransport({
#   service: "gmail",
#   auth: {
#     user: "shreya.claris@gmail.com",
#     pass: "bppsfowhnwnwkjig" // app password
#   }
# });

# const sendLowStockAlert = async (adminEmail, product) => {
#   console.log("Email service called for:", product.name);

#   const mailOptions = {
#     from: "SmartStock <shreya.claris@gmail.com>",
#     to: adminEmail,
#     subject: "🚨 LOW STOCK ALERT",
#     html: `
#       <h2>Low Stock Alert</h2>
#       <p><strong>Product:</strong> ${product.name}</p>
#       <p><strong>Category:</strong> ${product.category}</p>
#       <p><strong>Current Stock:</strong> ${product.stock}</p>
#       <p><strong>Low Stock Limit:</strong> ${product.lowStockLimit}</p>
#       <p>Please restock immediately.</p>
#     `
#   };

#   await transporter.sendMail(mailOptions);
# };

# module.exports = sendLowStockAlert;



import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Gmail SMTP config
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "shreya.claris@gmail.com"
EMAIL_PASS = "bppsfowhnwnwkjig"  # Gmail App Password


def send_low_stock_alert(admin_email, product):
    """
    Send low stock alert email
    product: dict (MongoDB product document)
    """

    print("Email service called for:", product.get("name"))

    subject = "🚨 LOW STOCK ALERT"

    html_body = f"""
    <h2>Low Stock Alert</h2>
    <p><strong>Product:</strong> {product.get("name")}</p>
    <p><strong>Category:</strong> {product.get("category")}</p>
    <p><strong>Current Stock:</strong> {product.get("stock")}</p>
    <p><strong>Low Stock Limit:</strong> {product.get("lowStockLimit")}</p>
    <p>Please restock immediately.</p>
    """

    # Create email
    msg = MIMEMultipart()
    msg["From"] = f"SmartStock <{EMAIL_USER}>"
    msg["To"] = admin_email
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        print("Low stock alert email sent successfully")

    except Exception as e:
        print("Email sending failed:", str(e))
