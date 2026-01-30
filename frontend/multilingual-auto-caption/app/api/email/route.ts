import { NextResponse } from 'next/server';
import nodemailer from 'nodemailer';
import { z } from 'zod';

const emailRequestSchema = z.object({
  email: z.string().email(),
  downloadUrl: z.string().url(),
});

type EmailRequest = z.infer<typeof emailRequestSchema>;

function getSmtpConfig() {
  const smtpHost = process.env.SMTP_HOST;
  const smtpPort = process.env.SMTP_PORT;
  const smtpUser = process.env.SMTP_USER;
  const smtpPass = process.env.SMTP_PASS;
  const smtpSecure = process.env.SMTP_SECURE === 'true';
  const smtpFrom = process.env.SMTP_FROM;
  const smtpFromName = process.env.SMTP_FROM_NAME;
  const smtpReplyTo = process.env.SMTP_REPLY_TO;

  if (!smtpHost || !smtpUser || !smtpPass || !smtpFrom) {
    return null;
  }

  const port = Number(smtpPort) || 587;

  return {
    host: smtpHost,
    port,
    secure: smtpSecure || port === 465,
    auth: {
      user: smtpUser,
      pass: smtpPass,
    },
    from: smtpFromName ? `"${smtpFromName}" <${smtpFrom}>` : smtpFrom,
    replyTo: smtpReplyTo,
  };
}

function buildEmailContent({ email, downloadUrl }: EmailRequest) {
  return {
    to: email,
    subject: 'Your Captioned Video is Ready!',
    text: `Hello,\n\nYour video has been successfully processed.\n\nYou can download it using the following link:\n${downloadUrl}\n\nThank you for using Multilingual Auto Caption!`,
    html: `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h2 style="color: #333;">Video Processing Complete</h2>
          <p>Hello,</p>
          <p>Your video has been successfully captioned and processed.</p>
          <div style="padding: 20px 0;">
              <a href="${downloadUrl}" style="background-color: #0070f3; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block;">Download Video</a>
          </div>
          <p style="color: #666; font-size: 14px;">Or copy this link to your browser:</p>
          <p style="background-color: #f5f5f5; padding: 10px; border-radius: 4px; font-family: monospace; word-break: break-all;">${downloadUrl}</p>
      </div>
    `,
  };
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const parsed = emailRequestSchema.safeParse(body);

    if (!parsed.success) {
      return NextResponse.json(
        { success: false, error: 'Invalid request payload', details: parsed.error.flatten() },
        { status: 400 },
      );
    }

    const { email, downloadUrl } = parsed.data;

    console.log(`[API/Email] Processing email request for: ${email}`);
    console.log(`[API/Email] Download URL: ${downloadUrl}`);

    const smtpConfig = getSmtpConfig();

    if (!smtpConfig) {
      console.error("[API/Email] SMTP configuration missing. Email not sent.");
      return NextResponse.json(
        { success: false, error: "SMTP configuration missing" },
        { status: 500 },
      );
    }

    const transporter = nodemailer.createTransport({
      host: smtpConfig.host,
      port: smtpConfig.port,
      secure: smtpConfig.secure,
      auth: smtpConfig.auth,
    });

    const mailOptions = {
      from: smtpConfig.from,
      replyTo: smtpConfig.replyTo,
      ...buildEmailContent({ email, downloadUrl }),
    };

    const info = await transporter.sendMail(mailOptions);
    console.log(`[API/Email] Email sent successfully. Message ID: ${info.messageId}`);

    return NextResponse.json({ success: true, messageId: info.messageId });

  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    console.error("[API/Email] Failed to send email:", error);
    return NextResponse.json({ success: false, error: message }, { status: 500 });
  }
}
