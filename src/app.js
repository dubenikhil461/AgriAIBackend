import  express from "express";
import cors from "cors";
import allroutes from './route.js'
const app = express();
const PORT = 8080;


const options = {
    origin:['http://localhost:5173'],
    Credential:true,
}
app.use(cors(options));
app.use(express.urlencoded({extended:true}))
app.use(express.json());


app.use('/api',allroutes)

// ✅ Route 1: Health Check
app.get("/", (req, res) => {
  res.json({ message: "Farmer AI Backend Running 🚀" });
});


app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
});
