# CryptoBot

Tento projekt implementuje kryptobota obchodujícího na Binance API s podporou manuálního i AI řízeného obchodování. Verze obsahuje následující pokročilé funkce:
- **Modely na vybraný pár s offline tréninkem a dynamickou správou** (LSTM model s více vrstvami, konverze do ONNX)
- **Break-even posun** – automatická úprava stop lossu při dosažení určitého zisku
- **Komplexní hedge strategie** – podpora současných long i short obchodů s diverzifikací rizika
- **Specifické zachytávání chyb** – vlastní výjimkové třídy a retry mechanismy
- **Nastavení obchodních parametrů** – loty, SL, TP, leverage (s možností manuálního či automatického nastavení)
- **AI predikce optimální velikosti pozice** – samostatný model pro lot sizing
- **Batch processing a optimalizace Binance API** – asynchroní načítání dat pro více párů
- **Adaptivní trailing stop-loss** – nastavení stop-lossu na základě aktuální volatility
- **Profilování paměti a circular buffers** – efektivní správa datových struktur
- **Optimalizace ONNX runtime** – automatická volba providerů a možnosti optimalizace
- **Auto-retraining modelu** – spuštění retrainingu na základě obchodních metrik
- **Komplexní monitorování síťového provozu a API rate limitů**

## Jak spustit projekt

1. **Instalace závislostí:**

   ```bash
   pip install -r requirements.txt
