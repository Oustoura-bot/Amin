import moment from 'moment-timezone';

let handler = async (m, { conn, text, usedPrefix, command, args, participants }) => {
    if (!text) throw `✳️ منشن المستخدم وأدخل عدد أيام الاشتراك.\n\n*مثال:*\n${usedPrefix + command} @${m.sender.split('@')[0]} 30`;

    let mentionedJid = m.mentionedJid[0];
    if (!mentionedJid) {
        // Try to parse number if no mention
        const number = text.split(' ')[0].replace(/[^0-9]/g, '');
        if (!number) throw `✳️ يرجى منشن المستخدم أو كتابة رقمه.\n\n*مثال:*\n${usedPrefix + command} @${m.sender.split('@')[0]} 30`;
        mentionedJid = number + '@s.whatsapp.net';
    }

    let days = parseInt(text.split(' ').pop());
    if (isNaN(days)) throw `✳️ عدد الأيام غير صالح. أدخل عدد الأيام.\n\n*مثال:*\n${usedPrefix + command} @${mentionedJid.split('@')[0]} 30`;

    if (!global.db.data.users[mentionedJid]) {
        global.db.data.users[mentionedJid] = {}; // Initialize user if not exists
    }

    let user = global.db.data.users[mentionedJid];
    const now = Date.now();
    const expiryDate = now + (days * 24 * 60 * 60 * 1000);

    // Initialize subscription fields if they don't exist
    if (!('subscription_active' in user)) user.subscription_active = false;
    if (!('subscription_start_date' in user)) user.subscription_start_date = null;
    if (!('subscription_end_date' in user)) user.subscription_end_date = null;

    user.subscription_active = true;
    user.subscription_start_date = now;
    user.subscription_end_date = expiryDate;

    const startDateStr = moment(now).tz('Africa/Casablanca').format('YYYY-MM-DD HH:mm:ss');
    const expiryDateStr = moment(expiryDate).tz('Africa/Casablanca').format('YYYY-MM-DD HH:mm:ss');

    // Notify Owner
    m.reply(`✅ تم إضافة اشتراك لمدة ${days} يوم للمستخدم @${mentionedJid.split('@')[0]}.\nينتهي في: ${expiryDateStr}`);

    // Notify User
    const notifyMessage = `🎉 تم تفعيل اشتراكك!\n\n*المدة:* ${days} يوم\n*تاريخ البدء:* ${startDateStr}\n*تاريخ الانتهاء:* ${expiryDateStr}\n\nاستمتع بميزات البوت!`;
    conn.sendMessage(mentionedJid, { text: notifyMessage });

};

handler.help = ['اضف_اشتراك @مستخدم <أيام>'];
handler.tags = ['owner'];
handler.command = /^(اضف_اشتراك|addsub|addsubscription)$/i;
handler.owner = true; // Only owner can use this command

export default handler;

