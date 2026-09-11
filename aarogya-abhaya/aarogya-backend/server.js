require("dotenv").config({ path: require("path").join(__dirname, "..", ".env") });
const axios = require("axios");
const express = require("express");
const bodyParser = require("body-parser");
const { Pool } = require("pg");
const session = require("express-session");
const nodemailer = require("nodemailer");
const bcrypt = require("bcrypt");
const { exec } = require("child_process");
const multer = require("multer");
const path = require("path");

let postureProcess = null; // stores currently running python process

const transporter = nodemailer.createTransport({
    service: "gmail",
    auth: {
        user: process.env.EMAIL_USER,
        pass: process.env.EMAIL_PASS
    }
});

const app = express();

// Multer configuration
const storage = multer.diskStorage({
    destination: "public/uploads",
    filename: (req, file, cb) => {
        const ext = file.originalname.split(".").pop();
        cb(null, `user_${req.session.user.id}.${ext}`);
    }
});

const upload = multer({ storage });

const videoStorage = multer.diskStorage({
    destination: "public/videos",
    filename: (req, file, cb) => {
        const ext = file.originalname.split(".").pop();
        cb(null, `video_${Date.now()}.${ext}`);
    }
});

const videoUpload = multer({
    storage: videoStorage,
    fileFilter: (req, file, cb) => {
        if (file.mimetype === "video/mp4") cb(null, true);
        else cb(new Error("Only MP4 videos allowed"));
    }
});

/* ---------------- MIDDLEWARE ---------------- */
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static("public"));

app.use(
    session({
        secret: process.env.SESSION_SECRET || "aarogya-secret",
        resave: false,
        saveUninitialized: false
    })
);

/* ---------------- DATABASE ---------------- */
const pool = new Pool({
    user: process.env.DB_USER || "postgres",
    host: process.env.DB_HOST || "localhost",
    database: process.env.DB_NAME || "aarogya_abhaya",
    password: process.env.DB_PASSWORD,
    port: parseInt(process.env.DB_PORT) || 5432
});

/* ============== AUTHENTICATION ENDPOINTS ============== */

app.get("/get-user", async (req, res) => {
    if (!req.session.user) {
        return res.status(401).json({ error: "Not logged in" });
    }

    try {
        const result = await pool.query(
            "SELECT id, full_name, role FROM users WHERE id = $1",
            [req.session.user.id]
        );
        res.json(result.rows[0]);
    } catch (err) {
        console.error("GET USER ERROR:", err);
        res.status(500).json({ error: "Server error" });
    }
});

app.post("/login", async (req, res) => {
    try {
        const { username, password } = req.body;
        const result = await pool.query(
            "SELECT * FROM users WHERE username = $1",
            [username]
        );

        if (result.rows.length === 0) {
            return res.status(400).json({ error: "User not found" });
        }

        const user = result.rows[0];
        let valid = false;

        if (user.password && user.password.startsWith("$2")) {
            valid = await bcrypt.compare(password, user.password);
        } else {
            valid = password === user.password;
        }

        if (!valid) {
            return res.status(401).json({ error: "Invalid password" });
        }

        const beneficiaryRoles = ["pregnant_woman", "teenager", "newborn"];
        if (beneficiaryRoles.includes(user.role)) {
            if (user.approval_status !== "approved" || user.lha_status !== "approved") {
                return res.status(403).json({
                    error: "Your account is pending approval. Please try logging in after verification."
                });
            }
        }

        req.session.user = {
            id: user.id,
            role: user.role
        };

        res.json({
            message: "Login successful",
            role: user.role,
            user_id: user.id
        });
    } catch (err) {
        console.log("LOGIN ERROR:", err);
        res.status(500).json({ error: "Server error" });
    }
});

app.post("/logout", (req, res) => {
    req.session.destroy(() => {
        res.json({ message: "Logged out" });
    });
});

app.get("/me", async (req, res) => {
    if (!req.session.user) {
        return res.status(401).json({ message: "Not logged in" });
    }

    const result = await pool.query(
        `SELECT 
        id, username, role, full_name, email, phone, dob, gender,
        blood_group, health_status, village, guardian, address, area, profile_photo
        FROM users WHERE id = $1`,
        [req.session.user.id]
    );
    res.json(result.rows[0]);
});

app.post("/change-password", async (req, res) => {
    if (!req.session.user) {
        return res.status(401).json({ message: "Not logged in" });
    }

    const { currentPassword, newPassword } = req.body;
    if (!currentPassword || !newPassword) {
        return res.status(400).json({ message: "All fields required" });
    }

    try {
        const result = await pool.query(
            "SELECT password FROM users WHERE id=$1",
            [req.session.user.id]
        );
        const user = result.rows[0];

        if (user.password !== currentPassword) {
            return res.status(400).json({ message: "Current password incorrect" });
        }

        await pool.query(
            "UPDATE users SET password=$1 WHERE id=$2",
            [newPassword, req.session.user.id]
        );

        req.session.destroy(() => {
            res.json({ success: true });
        });
    } catch (err) {
        console.error("PASSWORD CHANGE ERROR:", err);
        res.status(500).json({ message: "Server error" });
    }
});

app.post("/upload-photo", upload.single("photo"), async (req, res) => {
    if (!req.session.user) {
        return res.status(401).json({ message: "Not logged in" });
    }

    const photoPath = `/uploads/${req.file.filename}`;
    await pool.query(
        "UPDATE users SET profile_photo=$1 WHERE id=$2",
        [photoPath, req.session.user.id]
    );
    res.json({ success: true, photo: photoPath });
});

/* ============== REGISTRATION ENDPOINTS ============== */

app.post("/register", async (req, res) => {
    try {
        const { username, full_name, email, phone, address, area, password, role, code, jpha_id, lha_id } = req.body;
        const CODES = { asha_worker: "ASHA-2026", lha: "LHA-2026", jpha: "JPHA-2026" };

        if (!CODES[role]) return res.status(400).json({ error: "Invalid role selected" });
        if (code !== CODES[role]) return res.status(403).json({ error: "Invalid Registration Code" });

        const hashed = await bcrypt.hash(password, 10);

        if (role === "asha_worker") {
            if (!jpha_id) return res.status(400).json({ error: "JPHA must be selected for ASHA Worker" });
            const check = await pool.query("SELECT id FROM users WHERE id=$1 AND role='jpha'", [jpha_id]);
            if (check.rows.length === 0) return res.status(400).json({ error: "Invalid JPHA selected" });

            await pool.query(
                `INSERT INTO users (username, full_name, email, phone, address, area, password, role, jpha_id)
                 VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)`,
                [username, full_name, email, phone, address, area, hashed, role, jpha_id]
            );
            return res.json({ message: "ASHA Worker Registration Successful" });
        }

        if (role === "jpha") {
            if (!lha_id) return res.status(400).json({ error: "LHA must be selected for JPHA" });
            const checkLHA = await pool.query("SELECT id FROM users WHERE id=$1 AND role='lha'", [lha_id]);
            if (checkLHA.rows.length === 0) return res.status(400).json({ error: "Invalid LHA selected" });

            await pool.query(
                `INSERT INTO users (username, full_name, email, phone, address, area, password, role, lha_id)
                 VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)`,
                [username, full_name, email, phone, address, area, hashed, role, lha_id]
            );
            return res.json({ message: "JPHA Registration Successful" });
        }

        if (role === "lha") {
            await pool.query(
                `INSERT INTO users (username, full_name, email, phone, address, area, password, role)
                 VALUES ($1,$2,$3,$4,$5,$6,$7,$8)`,
                [username, full_name, email, phone, address, area, hashed, role]
            );
            return res.json({ message: "LHA Registration Successful" });
        }

        res.json({ message: "Registration Successful" });
    } catch (err) {
        console.log("REGISTER ERROR:", err);
        res.status(500).json({ error: "Server error" });
    }
});

app.post("/register-beneficiary", async (req, res) => {
    if (!req.session.user || req.session.user.role !== "asha_worker") {
        return res.status(403).json({ message: "Unauthorized" });
    }

    try {
        const {
            username, password, role, full_name = "", email = "", phone = "", dob,
            blood_group = "", address = "", area = "", village = "", guardian = "", gender = ""
        } = req.body;

        const hashedPassword = await bcrypt.hash(password, 10);
        const asha_id = req.session.user.id;

        if (!["pregnant_woman", "teenager", "newborn"].includes(role)) {
            return res.status(400).json({ message: "Invalid beneficiary role" });
        }

        const result = await pool.query(`
            INSERT INTO users
            (username, password, role, created_by, full_name, email, phone, dob,
            blood_group, address, area, village, guardian, gender, approval_status)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,'pending')
            RETURNING id, dob
        `, [
            username, hashedPassword, role, asha_id, full_name, email, phone, dob,
            blood_group, address, area, village, guardian, gender
        ]);

        const new_user_id = result.rows[0].id;
        const newborn_dob = result.rows[0].dob;

        if (role === "newborn") {
            await generateVaccinationSchedule(
    new_user_id,
    newborn_dob,
    req.session.user.id
);
        }

        res.json({ success: true, message: "Beneficiary registered successfully" });
    } catch (err) {
        console.error("REGISTER ERROR:", err);
        res.status(500).json({ success: false, message: "Backend registration error" });
    }
});

async function generateVaccinationSchedule(newbornId, dob, recordedBy) {
    const birthDate = new Date(dob);
    const vaccines = [
        { name: "BCG", days: 0 },
        { name: "OPV-0", days: 0 },
        { name: "Hepatitis B-0", days: 0 },
        { name: "Pentavalent-1", days: 42 },
        { name: "OPV-1", days: 42 },
        { name: "Pentavalent-2", days: 70 },
        { name: "OPV-2", days: 70 },
        { name: "Pentavalent-3", days: 98 },
        { name: "OPV-3", days: 98 },
        { name: "Measles-Rubella", days: 270 }
    ];

    for (let v of vaccines) {
        let dueDate = new Date(birthDate);
        dueDate.setDate(dueDate.getDate() + v.days);
        await pool.query(
            `INSERT INTO vaccinations 
            (newborn_id, vaccine_name, due_date, status, recorded_by) 
            VALUES ($1, $2, $3, 'pending', $4)`,
            [newbornId, v.name, dueDate, recordedBy || 1]
        );
    }
}

/* ============== NOTICES ENDPOINTS ============== */

app.post("/notices", async (req, res) => {
    if (!req.session.user || req.session.user.role !== "asha_worker") {
        return res.status(403).json({ message: "Unauthorized" });
    }

    const { message, targetRoles } = req.body;
    if (!message || !Array.isArray(targetRoles) || targetRoles.length === 0) {
        return res.status(400).json({ message: "Message and roles required" });
    }

    try {
        await pool.query(
            `INSERT INTO notices (message, created_by, target_roles) VALUES ($1, $2, $3)`,
            [message, req.session.user.id, targetRoles]
        );
        res.json({ success: true });
    } catch (err) {
        console.error("Notice error:", err);
        res.status(500).json({ message: "Server error" });
    }
});

app.get("/notices", async (req, res) => {
    if (!req.session.user) {
        return res.status(401).json([]);
    }

    const { id, role } = req.session.user;

    try {
        if (role === "asha_worker") {
            const result = await pool.query(`
                SELECT n.id, n.message, n.target_roles, n.created_at, u.full_name AS sender_name
                FROM notices n
                JOIN users u ON u.id = n.created_by
                WHERE n.created_by = $1
                ORDER BY n.created_at DESC
            `, [id]);
            return res.json(result.rows);
        }

        const result = await pool.query(`
            SELECT n.message, u.full_name AS sender_name, n.created_at
            FROM notices n
            JOIN users u ON u.id = n.created_by
            WHERE n.created_by = (SELECT created_by FROM users WHERE id = $1)
            AND ($2 = ANY(n.target_roles) OR 'all' = ANY(n.target_roles))
            ORDER BY n.created_at DESC
        `, [id, role]);

        res.json(result.rows);
    } catch (err) {
        console.error("GET NOTICE ERROR:", err);
        res.status(500).json([]);
    }
});

app.delete("/notices/:id", async (req, res) => {
    if (!req.session.user || req.session.user.role !== "asha_worker") {
        return res.status(403).json({ message: "Unauthorized" });
    }

    try {
        await pool.query("DELETE FROM notices WHERE id = $1", [req.params.id]);
        res.json({ success: true });
    } catch (err) {
        console.error("DELETE NOTICE ERROR:", err);
        res.status(500).json({ message: "Failed to delete notice" });
    }
});

/* ============== VIDEO ENDPOINTS ============== */

app.post("/asha/upload-video", videoUpload.single("video"), async (req, res) => {
    if (!req.session.user || req.session.user.role !== "asha_worker") {
        return res.status(403).json({ message: "Unauthorized" });
    }

    const { title, description, category } = req.body;
    if (!title || !category) {
        return res.status(400).json({ message: "Title & category required" });
    }

    const videoPath = `/videos/${req.file.filename}`;

    try {
        await pool.query(
            `INSERT INTO videos (title, description, category, video_path, uploaded_by)
             VALUES ($1,$2,$3,$4,$5)`,
            [title, description, category, videoPath, req.session.user.id]
        );
        res.json({ success: true });
    } catch (err) {
        console.error("VIDEO UPLOAD ERROR:", err);
        res.status(500).json({ message: "Server error" });
    }
});

app.get("/videos/:category", async (req, res) => {
    if (!req.session.user) {
        return res.status(401).json({ message: "Not logged in" });
    }

    const category = req.params.category;
    const userId = req.session.user.id;

    try {
        const user = await pool.query(
            "SELECT created_by FROM users WHERE id=$1",
            [userId]
        );
        const ashaId = user.rows[0].created_by;

        const videos = await pool.query(
            `SELECT * FROM videos
             WHERE category=$1 AND uploaded_by=$2
             ORDER BY created_at DESC`,
            [category, ashaId]
        );
        res.json(videos.rows);
    } catch (err) {
        console.error("VIDEO FETCH ERROR:", err);
        res.status(500).json({ message: "Server error" });
    }
});

app.get("/asha/my-videos", async (req, res) => {
    if (!req.session.user || req.session.user.role !== "asha_worker") {
        return res.status(403).json({ message: "Unauthorized" });
    }

    try {
        const result = await pool.query(
            `SELECT id, title, category, video_path, created_at
             FROM videos WHERE uploaded_by = $1
             ORDER BY created_at DESC`,
            [req.session.user.id]
        );
        res.json(result.rows);
    } catch (err) {
        console.error("FETCH MY VIDEOS ERROR:", err);
        res.status(500).json({ message: "Server error" });
    }
});

app.delete("/asha/delete-video/:id", async (req, res) => {
    if (!req.session.user || req.session.user.role !== "asha_worker") {
        return res.status(403).json({ message: "Unauthorized" });
    }

    try {
        const result = await pool.query(
            `SELECT video_path FROM videos WHERE id=$1 AND uploaded_by=$2`,
            [req.params.id, req.session.user.id]
        );

        if (result.rows.length === 0) {
            return res.status(404).json({ message: "Video not found" });
        }

        await pool.query(`DELETE FROM videos WHERE id=$1`, [req.params.id]);
        res.json({ success: true });
    } catch (err) {
        console.error("DELETE VIDEO ERROR:", err);
        res.status(500).json({ message: "Server error" });
    }
});

/* ============== TRACKING ENDPOINTS ============== */

app.get("/asha/beneficiaries", async (req, res) => {
    if (!req.session.user || req.session.user.role !== "asha_worker") {
        return res.status(403).json({ error: "Unauthorized" });
    }

    try {
        const result = await pool.query(`
            SELECT id, username, role, full_name, email, phone, dob,
                   profile_photo, approval_status, lha_status
            FROM users WHERE created_by = $1
            ORDER BY id DESC
        `, [req.session.user.id]);
        res.json(result.rows);
    } catch (err) {
        console.error("Tracking error:", err);
        res.status(500).json({ error: "Server error" });
    }
});

/* ============== VACCINATION ENDPOINTS ============== */

app.get("/asha/vaccinations", async (req, res) => {
    if (!req.session.user || req.session.user.role !== "asha_worker") {
        return res.status(403).json({ message: "Unauthorized" });
    }

    try {
        const result = await pool.query(`
            SELECT v.id, u.full_name, v.vaccine_name, v.due_date, v.status,
                   CASE
                       WHEN v.status='pending' AND v.due_date < CURRENT_DATE THEN 'overdue'
                       WHEN v.status='pending' AND v.due_date <= CURRENT_DATE + INTERVAL '7 days' THEN 'due_soon'
                       ELSE 'normal'
                   END as alert_status
            FROM vaccinations v
            JOIN users u ON v.newborn_id = u.id
            WHERE u.created_by = $1
            ORDER BY v.due_date ASC
        `, [req.session.user.id]);
        res.json(result.rows);
    } catch (err) {
        console.error(err);
        res.status(500).json({ message: "Error fetching vaccines" });
    }
});

app.put("/asha/complete-vaccine/:id", async (req, res) => {
    if (!req.session.user || req.session.user.role !== "asha_worker") {
        return res.status(403).json({ message: "Unauthorized" });
    }

    try {
        await pool.query(`
            UPDATE vaccinations
            SET status = 'completed', given_date = CURRENT_DATE
            WHERE id = $1
        `, [req.params.id]);
        res.json({ success: true });
    } catch (err) {
        console.error(err);
        res.status(500).json({ message: "Error updating vaccine" });
    }
});

app.post("/asha/add-vaccine", async (req, res) => {
    if (!req.session.user || req.session.user.role !== "asha_worker") {
        return res.status(403).json({ error: "Unauthorized" });
    }

    const { newborn_id, vaccine_name, due_date } = req.body;
    try {
        await pool.query(
            `INSERT INTO vaccinations (newborn_id, vaccine_name, due_date, recorded_by)
             VALUES ($1,$2,$3,$4)`,
            [newborn_id, vaccine_name, due_date, req.session.user.id]
        );
        res.json({ success: true });
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: "Server error" });
    }
});

app.post("/asha/mark-vaccine/:id", async (req, res) => {
    if (!req.session.user || req.session.user.role !== "asha_worker") {
        return res.status(403).json({ error: "Unauthorized" });
    }

    try {
        await pool.query(
            `UPDATE vaccinations SET status='completed', given_date=NOW() WHERE id=$1`,
            [req.params.id]
        );
        res.json({ success: true });
    } catch (err) {
        res.status(500).json({ error: "Server error" });
    }
});

app.get("/asha/newborns", async (req, res) => {
    if (!req.session.user || req.session.user.role !== "asha_worker") {
        return res.status(403).json([]);
    }

    const result = await pool.query(
        `SELECT id, full_name FROM users WHERE created_by=$1 AND role='newborn'`,
        [req.session.user.id]
    );
    res.json(result.rows);
});

app.get("/asha/vaccine-alerts", async (req, res) => {
    if (!req.session.user || req.session.user.role !== "asha_worker") {
        return res.status(403).json({});
    }

    const overdue = await pool.query(`
        SELECT COUNT(*) FROM vaccinations
        WHERE status='pending' AND due_date < CURRENT_DATE
    `);

    const dueSoon = await pool.query(`
        SELECT COUNT(*) FROM vaccinations
        WHERE status='pending' 
        AND due_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
    `);

    res.json({
        overdue: overdue.rows[0].count,
        dueSoon: dueSoon.rows[0].count
    });
});

app.get("/api/newborn/vaccines", async (req, res) => {
    const newbornId = req.session.user.id;
    const baby = await pool.query(
        "SELECT full_name, dob FROM users WHERE id = $1",
        [newbornId]
    );
    const vaccines = await pool.query(
        "SELECT * FROM vaccinations WHERE newborn_id = $1 ORDER BY due_date",
        [newbornId]
    );
    res.json({ baby: baby.rows[0], vaccines: vaccines.rows });
});

/* ============== JPHA ENDPOINTS ============== */

app.get("/jpha/stats", async (req, res) => {
    if (!req.session.user || req.session.user.role !== "jpha")
        return res.status(403).json({});

    const jphaId = req.session.user.id;

    const asha = await pool.query(
        `SELECT COUNT(*) FROM users WHERE role='asha_worker' AND jpha_id=$1`,
        [jphaId]
    );

    const pending = await pool.query(
        `SELECT COUNT(*)
         FROM users u JOIN users a ON u.created_by=a.id
         WHERE a.jpha_id=$1 AND u.approval_status='pending'
         AND u.role IN ('pregnant_woman','teenager','newborn')`,
        [jphaId]
    );

    const approved = await pool.query(
        `SELECT COUNT(*)
         FROM users u JOIN users a ON u.created_by=a.id
         WHERE a.jpha_id=$1 AND u.approval_status='approved'
         AND u.role IN ('pregnant_woman','teenager','newborn')`,
        [jphaId]
    );

    res.json({
        asha: asha.rows[0].count,
        pending: pending.rows[0].count,
        approved: approved.rows[0].count
    });
});

app.get("/jpha/asha-workers", async (req, res) => {
    if (!req.session.user || req.session.user.role !== "jpha") return res.status(403).json([]);

    const result = await pool.query(
        `SELECT id, full_name, email, username, phone, address
         FROM users WHERE role='asha_worker' AND jpha_id=$1`,
        [req.session.user.id]
    );
    res.json(result.rows);
});

app.get("/jpha/beneficiaries", async (req, res) => {
    try {
        if (!req.session.user || req.session.user.role !== "jpha") {
            return res.status(403).json({ error: "Unauthorized" });
        }

        const jphaId = req.session.user.id;
        const result = await pool.query(
            `SELECT u.id, u.full_name, u.phone, u.address, u.dob, u.role, u.approval_status,
                    a.full_name AS registered_by
             FROM users u
             JOIN users a ON u.created_by = a.id
             WHERE a.jpha_id = $1 AND u.role IN ('pregnant_woman', 'teenager', 'newborn')
             ORDER BY u.id DESC`,
            [jphaId]
        );
        res.json(result.rows);
    } catch (err) {
        console.error("Fetch beneficiaries error:", err);
        res.status(500).json({ error: "Server error" });
    }
});

app.post("/jpha/approve-beneficiary/:id", async (req, res) => {
    if (!req.session.user || req.session.user.role !== "jpha") {
        return res.status(403).json({ error: "Unauthorized" });
    }

    const beneficiaryId = req.params.id;
    const { action } = req.body;

    if (!["approve", "reject"].includes(action)) {
        return res.status(400).json({ error: "Invalid action" });
    }

    try {
        const result = await pool.query(
            `UPDATE users u
             SET approval_status = $1
             FROM users a
             WHERE u.created_by = a.id AND a.jpha_id = $2 AND u.id = $3
             RETURNING u.id, u.full_name, u.approval_status`,
            [action === "approve" ? "approved" : "rejected", req.session.user.id, beneficiaryId]
        );

        if (result.rows.length === 0) {
            return res.status(404).json({ error: "Beneficiary not found or not under your ASHA" });
        }

        res.json({ success: true, beneficiary: result.rows[0] });
    } catch (err) {
        console.error("Approval error:", err);
        res.status(500).json({ error: "Server error" });
    }
});

/* ============== LHA ENDPOINTS ============== */

app.get("/lha/stats", async (req, res) => {
    try {
        const totalResult = await pool.query(
            `SELECT COUNT(*) FROM users WHERE role IN ('pregnant_woman','teenager','newborn')`
        );

        const pendingResult = await pool.query(
            `SELECT COUNT(*) FROM users
             WHERE role IN ('pregnant_woman','teenager','newborn')
             AND approval_status='approved' AND lha_status='pending'`
        );

        res.json({
            total_beneficiaries: totalResult.rows[0].count,
            pending_approvals: pendingResult.rows[0].count
        });
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: "Server error" });
    }
});

app.get("/lha/jphas", async (req, res) => {
    if (!req.session.user || req.session.user.role !== "lha") return res.status(403).json([]);

    try {
        const lhaId = req.session.user.id;
        const result = await pool.query(
            `SELECT id, full_name, email, phone, username
             FROM users WHERE role='jpha' AND lha_id=$1`,
            [lhaId]
        );
        res.json(result.rows);
    } catch (err) {
        console.error("LHA JPHAS ERROR:", err);
        res.status(500).json([]);
    }
});

app.get("/lha/beneficiaries", async (req, res) => {
    if (!req.session.user || req.session.user.role !== "lha")
        return res.status(403).json([]);

    const lhaId = req.session.user.id;

    const result = await pool.query(
        `SELECT u.id, u.full_name, u.phone, u.address, u.dob, u.role,
                u.approval_status, u.lha_status, j.full_name AS approved_by
         FROM users u
         JOIN users a ON u.created_by = a.id
         JOIN users j ON a.jpha_id = j.id
         WHERE j.lha_id = $1 AND u.approval_status='approved'
         AND u.role IN ('pregnant_woman','teenager','newborn')
         ORDER BY u.id DESC`,
        [lhaId]
    );
    res.json(result.rows);
});

app.get("/lha/asha-workers", async (req, res) => {
    if (!req.session.user || req.session.user.role !== "lha")
        return res.status(403).json([]);

    try {
        const lhaId = req.session.user.id;
        const result = await pool.query(
            `SELECT a.id, a.full_name, a.email, a.phone, j.full_name AS jpha_name
             FROM users a
             JOIN users j ON a.jpha_id = j.id
             WHERE a.role='asha_worker' AND j.lha_id=$1
             ORDER BY a.full_name`,
            [lhaId]
        );
        res.json(result.rows);
    } catch (err) {
        console.error("LHA ASHA ERROR:", err);
        res.status(500).json([]);
    }
});

app.post("/lha/update-beneficiary-status", async (req, res) => {
    if (!req.session.user || req.session.user.role !== "lha") {
        return res.status(403).json({ success: false });
    }

    const { id, status } = req.body;
    try {
        await pool.query(`UPDATE users SET lha_status=$1 WHERE id=$2`, [status, id]);
        res.json({ success: true });
    } catch (err) {
        console.error(err);
        res.json({ success: false });
    }
});

/* ============== UTILITY ENDPOINTS ============== */

app.get("/get-jphas", async (req, res) => {
    try {
        const result = await pool.query(
            "SELECT id, full_name FROM users WHERE role='jpha'"
        );
        res.json(result.rows);
    } catch (err) {
        console.error("GET JPHAs ERROR:", err);
        res.status(500).json([]);
    }
});

app.get("/api/jphas", async (req, res) => {
    try {
        const result = await pool.query("SELECT id, full_name FROM users WHERE role='jpha'");
        res.json(result.rows);
    } catch (err) {
        console.error("JPHAs fetch error:", err);
        res.status(500).json({ error: "Failed to fetch JPHAs" });
    }
});

app.get("/get-lhas", async (req, res) => {
    try {
        const result = await pool.query(
            "SELECT id, full_name FROM users WHERE role='lha' ORDER BY full_name"
        );
        res.json(result.rows);
    } catch (err) {
        console.error("GET LHAs ERROR:", err);
        res.status(500).json({ error: "Failed to fetch LHAs" });
    }
});

app.get("/get-asha-workers", async (req, res) => {
    if (!req.session.user || req.session.user.role !== "jpha") {
        return res.status(403).json([]);
    }

    const jphaId = req.session.user.id;
    const result = await pool.query(
        `SELECT id, full_name FROM users WHERE role='asha_worker' AND jpha_id=$1`,
        [jphaId]
    );
    res.json(result.rows);
});

/* ============== FORGOT PASSWORD ENDPOINTS ============== */

app.post("/forgot-password", async (req, res) => {
    const { username } = req.body;

    try {
        const userRes = await pool.query(
            "SELECT email FROM users WHERE username=$1",
            [username]
        );

        if (userRes.rows.length === 0) {
            return res.status(400).json({ message: "User not found" });
        }

        const email = userRes.rows[0].email;
        if (!email) {
            return res.status(400).json({ message: "Email not registered" });
        }

        const otp = Math.floor(100000 + Math.random() * 900000).toString();
        const expiry = new Date(Date.now() + 5 * 60 * 1000);

        await pool.query(
            "UPDATE users SET otp=$1, otp_expiry=$2 WHERE username=$3",
            [otp, expiry, username]
        );

        await transporter.sendMail({
            from: `AAROGYA ABHAYA <${process.env.EMAIL_USER}>`,
            to: email,
            subject: "Password Reset OTP",
            html: `
                <h3>Password Reset</h3>
                <p>Your OTP is:</p>
                <h2>${otp}</h2>
                <p>This OTP is valid for 5 minutes.</p>
            `
        });

        res.json({ success: true, message: "OTP sent to email" });
    } catch (err) {
        console.error("OTP ERROR:", err);
        res.status(500).json({ message: "Server error" });
    }
});

app.post("/reset-password", async (req, res) => {
    const { username, otp, newPassword } = req.body;

    const result = await pool.query(
        "SELECT otp, otp_expiry FROM users WHERE username=$1",
        [username]
    );

    if (result.rows.length === 0) {
        return res.status(400).json({ message: "User not found" });
    }

    const user = result.rows[0];

    if (user.otp !== otp || new Date() > user.otp_expiry) {
        return res.status(400).json({ message: "Invalid or expired OTP" });
    }

    await pool.query(
        "UPDATE users SET password=$1, otp=NULL, otp_expiry=NULL WHERE username=$2",
        [newPassword, username]
    );

    res.json({ success: true, message: "Password updated" });
});

/* ============== AI PREDICTION ENDPOINT ============== */

app.post("/api/newborn/predict", async (req, res) => {
    try {
        const response = await axios.post(
            "http://127.0.0.1:5000/predict",
            req.body
        );
        res.json(response.data);
    } catch (error) {
        console.error("AI Prediction Error:", error.message);
        res.status(500).json({ error: "AI server not running" });
    }
});

/* ============== CAMERA MODULE ENDPOINTS ============== */

// Simple test endpoint
app.get("/test", (req, res) => {
    res.json({ message: "Server is working!", status: "ok" });
});

// Start squat detection
app.get("/start-squat", (req, res) => {
    console.log("Starting squat detection...");
    
    // Send response immediately
    res.status(200).json({ 
        success: true, 
        message: "Starting squat detection. Please check for new window." 
    });
    
    // Execute Python script
    const pythonProcess = exec(
        'python "' + path.join(__dirname, '..', 'pregnant-module', 'backend', 'posture', 'live_posture_detection.py') + '"',
        { 
            env: { 
                ...process.env, 
                PYTHONIOENCODING: 'utf-8',
                TF_CPP_MIN_LOG_LEVEL: '2' 
            } 
        },
        (error, stdout, stderr) => {
            if (error) {
                console.error(`Python error: ${error.message}`);
            }
            if (stderr) {
                console.error(`Python stderr: ${stderr}`);
            }
            if (stdout) {
                console.log(`Python stdout: ${stdout}`);
            }
        }
    );
    
    pythonProcess.on('spawn', () => {
        console.log("Python process spawned successfully");
    });
    
    pythonProcess.on('error', (err) => {
        console.error("Failed to spawn Python process:", err);
    });
});

// Start sitting detection
app.get("/start-sitting", (req, res) => {
    console.log("Starting sitting posture detection...");
    
    // Send response immediately
    res.status(200).json({ 
        success: true, 
        message: "Starting sitting detection. Please check for new window." 
    });
    
    // Execute Python script
    const pythonProcess = exec(
        'python "' + path.join(__dirname, '..', 'pregnant-module', 'backend', 'sitting_posture_module', 'live_sitting_posture.py') + '"',
        { 
            env: { 
                ...process.env, 
                PYTHONIOENCODING: 'utf-8' 
            } 
        },
        (error, stdout, stderr) => {
            if (error) {
                console.error(`Python error: ${error.message}`);
            }
            if (stderr) {
                console.error(`Python stderr: ${stderr}`);
            }
            if (stdout) {
                console.log(`Python stdout: ${stdout}`);
            }
        }
    );
    
    pythonProcess.on('spawn', () => {
        console.log("Python process spawned successfully");
    });
    
    pythonProcess.on('error', (err) => {
        console.error("Failed to spawn Python process:", err);
    });
});

/* ============== START SERVER ============== */

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log("=".repeat(50));
    console.log(`✅ Server running on http://localhost:${PORT}`);
    console.log(`✅ Test endpoint: http://localhost:${PORT}/test`);
    console.log("=".repeat(50));
});