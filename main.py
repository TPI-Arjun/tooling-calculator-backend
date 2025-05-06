from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/quote")
async def generate_quote(
    file: UploadFile = File(...),
    volume: int = Form(...),
    material: str = Form(...),
    cavities: int = Form(...),
    steel: str = Form(...),
    process: str = Form(...)
):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = tmp.name
        content = await file.read()
        tmp.write(content)

    part_weight_g = 35
    runner_weight = 0.1 * part_weight_g
    steel_rate = {"Orvar Supreme": 1100, "Stavax": 1250, "C45": 250}[steel]
    core_cavity_steel_kg = 45 + cavities * 3
    mould_base_steel_kg = 60 + cavities * 5

    cost = {
        "core_cavity_steel": core_cavity_steel_kg * steel_rate,
        "mould_base_steel": mould_base_steel_kg * 250,
        "core_cavity_machining": 35 * 420,
        "mould_base_machining": 20 * 420,
        "edm": 10 * 450,
        "wirecut": 6 * 700,
        "boughtout": 45000,
        "fixed": 100000,
    }
    total_inr = sum(cost.values())
    total_usd = round(total_inr / 78, 2)

    quote = f"""
    📦 Tooling Quote for {cavities} cavity mould

    ➤ Material: {material}
    ➤ Moulding Process: {process}
    ➤ Steel: {steel}
    ➤ Annual Volume: {volume}

    💡 Estimated Complexity: 3/4
    🧊 Tonnage Required: 120–150T
    ⏱ Cycle Time: ~30s
    🧮 Runner Weight: {runner_weight:.1f}g

    💰 Cost Breakdown (INR):
    - Core & Cavity Steel: ₹{cost['core_cavity_steel']:,}
    - Mould Base Steel: ₹{cost['mould_base_steel']:,}
    - Core/Cavity Machining (VMC): ₹{cost['core_cavity_machining']:,}
    - Mould Base Machining (VMC): ₹{cost['mould_base_machining']:,}
    - EDM: ₹{cost['edm']:,}
    - Wirecut: ₹{cost['wirecut']:,}
    - Bought-out Parts: ₹{cost['boughtout']:,}
    - Design + Assembly + Trials: ₹{cost['fixed']:,}

    ✅ Total Cost: ₹{total_inr:,} / ${total_usd}
    """

    os.remove(tmp_path)
    return {"quote": quote.strip()}
