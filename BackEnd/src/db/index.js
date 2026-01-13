import pg from 'pg';
const { Pool } = pg;

const pool = new Pool({
  connectionString: process.env.DATABASE_URL
});

const dbConnect = async () => {
    try {
        const client = await pool.connect();
        console.log(`\n PostgreSQL Connected! Host: ${client.host}`);
        client.release();
    } catch (error) {
        console.error("PostgreSQL Connection Failed:", error);
        process.exit(1);
    }
}

export { pool };
export default dbConnect;