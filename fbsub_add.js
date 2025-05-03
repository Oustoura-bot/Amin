import fs from 'fs';
import moment from 'moment-timezone';

const SUBS_FILE = './subscriptions.json'; // Store in the root directory of the bot

// Function to read subscriptions
function readSubscriptions() {
    try {
        if (fs.existsSync(SUBS_FILE)) {
            const data = fs.readFileSync(SUBS_FILE, 'utf8');
            return JSON.parse(data);
        } else {
            return {}; // Return empty object if file doesn't exist
        }
    } catch (error) {
        console.error("Error reading subscriptions file:", error);
        return {}; // Return empty object on error
    }
}

// Function to write subscriptions
function writeSubscriptions(data) {
    try {
        fs.writeFileSync(SUBS_FILE, JSON.stringify(data, null, 2)); // Pretty print JSON
    } catch (error) {
        console.error("Error writing subscriptions file:", error);
    }
}

let handler = async (m, { conn, args, text, command, usedPrefix }) => {
    if (!m.mentionedJid || m.mentionedJid.length === 0) {
        return m.reply(`⚠️ يرجى الإشارة (mention) إلى المستخدم الذي تريد إضافة/تحديث اشتراكه.\nمثال: ${usedPrefix + command} @المستخدم 30`);
    }

    let userId = m.mentionedJid[0];
    let daysToAdd = parseInt(args[1]);

    if (isNaN(daysToAdd) || daysToAdd <= 0) {
        return m.reply(`⚠️ يرجى تحديد عدد أيام صالح للاشتراك (أكبر من صفر).\nمثال: ${usedPrefix + command} @المستخدم 30`);
    }

    let subscriptions = readSubscriptions();
    const expiryDate = moment().add(daysToAdd, 'days').toISOString(); // Store expiry date in ISO format (UTC)

    subscriptions[userId] = {
        expiry: expiryDate,
        addedBy: m.sender, // Store who added the sub
        addedOn: moment().toISOString()
    };

    writeSubscriptions(subscriptions);

    const expiryDateFormatted = moment(expiryDate).tz('Africa/Casablanca').format('YYYY-MM-DD HH:mm'); // Format for display

    m.reply(`✅ تم تحديث اشتراك المستخدم @${userId.split('@')[0]} بنجاح.
تاريخ الانتهاء الجديد: ${expiryDateFormatted} (لمدة ${daysToAdd} يومًا)`);

    // Optionally notify the user who received the subscription
    conn.reply(userId, `🎉 تهانينا! لقد قام المالك بتحديث اشتراكك في خدمة البث المباشر.
صلاحيتك تنتهي في: ${expiryDateFormatted}`, m); // Send notification to the user

};

handler.help = ['addsub @user <days>'];
handler.tags = ['owner', 'streaming'];
handler.command = ['addsub', 'اضافة_اشتراك'];
handler.owner = true; // Only owner can add subscriptions

export default handler;

