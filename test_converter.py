#!/usr/bin/env python3
"""
Тестовий скрипт для перевірки функціональності Fintom8 MCP сервера
"""
import asyncio
import httpx
from pathlib import Path

# URL конвертера
CONVERTER_URL = "https://fintom8converter-prod.ey.r.appspot.com/backend/converter-workflowv2/"


async def test_converter():
    """Тест конвертера PDF -> UBL"""
    print("🧪 Тестування ендпоінту конвертації PDF -> UBL\n")
    print(f"📍 URL: {CONVERTER_URL}\n")
    
    # Створимо простий тестовий запит без файлу
    # (очікуємо помилку, але це покаже що ендпоінт доступний)
    
    async with httpx.AsyncClient() as client:
        try:
            # Тест 1: Перевірка доступності ендпоінту
            print("1️⃣  Перевірка доступності ендпоінту...")
            
            data = {
                'invoice_format': 'ubl',
                'verbose_output': 'false',
                'gemini_model': 'gemini-3-flash-preview',
                'max_iterations': '3'
            }
            
            response = await client.post(
                CONVERTER_URL,
                data=data,
                timeout=30.0
            )
            
            print(f"   ✅ Статус відповіді: {response.status_code}")
            print(f"   📄 Тіло відповіді: {response.text[:200]}...\n")
            
        except httpx.HTTPStatusError as e:
            print(f"   ⚠️  HTTP помилка {e.response.status_code}: {e.response.text[:200]}")
            print(f"   ℹ️  Це нормально без PDF файлу\n")
            
        except Exception as e:
            print(f"   ❌ Помилка: {str(e)}\n")
    
    print("=" * 70)
    print("✨ Тест завершено!")
    print("\n📝 Для повноцінного тестування:")
    print("   1. Додайте PDF інвойс в проект")
    print("   2. Використайте convert_pdf_to_invoice(pdf_path='...')")
    print("   3. Або підключіть MCP сервер до Claude Desktop")


if __name__ == "__main__":
    asyncio.run(test_converter())
