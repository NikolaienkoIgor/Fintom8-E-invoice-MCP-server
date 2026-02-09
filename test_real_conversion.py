#!/usr/bin/env python3
"""
Повний тест конвертації PDF інвойсу в UBL формат
"""
import asyncio
import httpx
from pathlib import Path
import json
from datetime import datetime

# URL конвертера
CONVERTER_URL = "https://fintom8converter-prod.ey.r.appspot.com/backend/converter-workflowv2/"

# Шлях до PDF файлу
PDF_PATH = "/Users/maximdoroshenko/Desktop/fintom8-mcp-server/EN16931_Physiotherapeut.pdf"


async def test_pdf_conversion():
    """Повний тест конвертації PDF -> UBL"""
    print("=" * 80)
    print("🧪 ТЕСТУВАННЯ КОНВЕРТАЦІЇ PDF ІНВОЙСУ В UBL ФОРМАТ")
    print("=" * 80)
    print()
    
    # Перевірка наявності файлу
    pdf_file = Path(PDF_PATH)
    if not pdf_file.exists():
        print(f"❌ Файл не знайдено: {PDF_PATH}")
        return
    
    print(f"📄 Файл знайдено: {pdf_file.name}")
    print(f"📊 Розмір файлу: {pdf_file.stat().st_size / 1024:.2f} KB")
    print()
    
    # Читаємо PDF файл
    pdf_content = pdf_file.read_bytes()
    
    print("🚀 Запуск конвертації...")
    print(f"🔗 Ендпоінт: {CONVERTER_URL}")
    print()
    
    start_time = datetime.now()
    
    async with httpx.AsyncClient() as client:
        try:
            # Prepare multipart form data
            files = {
                'file': (pdf_file.name, pdf_content, 'application/pdf')
            }
            
            data = {
                'invoice_format': 'ubl',
                'verbose_output': 'true',  # Увімкнемо детальний вивід
                'gemini_model': 'gemini-3-flash-preview',
                'max_iterations': '3'
            }
            
            print("⚙️  Параметри конвертації:")
            print(f"   • Формат: {data['invoice_format']}")
            print(f"   • Gemini модель: {data['gemini_model']}")
            print(f"   • Макс. ітерацій: {data['max_iterations']}")
            print(f"   • Детальний вивід: {data['verbose_output']}")
            print()
            
            print("⏳ Відправка запиту... (це може зайняти 30-60 секунд)")
            
            response = await client.post(
                CONVERTER_URL,
                files=files,
                data=data,
                timeout=120.0  # 2 хвилини таймаут
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print()
            print("=" * 80)
            print("📊 РЕЗУЛЬТАТ")
            print("=" * 80)
            print()
            print(f"✅ Статус відповіді: {response.status_code}")
            print(f"⏱️  Час виконання: {duration:.2f} секунд")
            print()
            
            if response.status_code == 200:
                print("🎉 КОНВЕРТАЦІЯ УСПІШНА!")
                print()
                
                # Парсимо JSON відповідь
                try:
                    result = response.json()
                    
                    # Зберігаємо результат у файл
                    output_file = Path("conversion_result.json")
                    output_file.write_text(json.dumps(result, indent=2, ensure_ascii=False))
                    print(f"💾 Повний результат збережено в: {output_file.absolute()}")
                    print()
                    
                    # Виводимо ключову інформацію
                    print("📋 Структура відповіді:")
                    for key in result.keys():
                        print(f"   • {key}")
                    print()
                    
                    # Якщо є UBL XML - зберігаємо окремо
                    if 'ubl_xml' in result:
                        ubl_file = Path("converted_invoice.xml")
                        ubl_file.write_text(result['ubl_xml'])
                        print(f"📄 UBL XML збережено в: {ubl_file.absolute()}")
                        print(f"📏 Розмір UBL: {len(result['ubl_xml'])} символів")
                    elif 'xml' in result:
                        ubl_file = Path("converted_invoice.xml")
                        ubl_file.write_text(result['xml'])
                        print(f"📄 XML збережено в: {ubl_file.absolute()}")
                        print(f"📏 Розмір XML: {len(result['xml'])} символів")
                    
                    # Виводимо перші 500 символів відповіді
                    print()
                    print("🔍 Перегляд відповіді (перші 500 символів):")
                    print("-" * 80)
                    print(json.dumps(result, indent=2, ensure_ascii=False)[:500] + "...")
                    print("-" * 80)
                    
                except json.JSONDecodeError:
                    print("⚠️  Відповідь не є JSON. Ось перші 1000 символів:")
                    print(response.text[:1000])
                    
            else:
                print(f"❌ ПОМИЛКА КОНВЕРТАЦІЇ")
                print(f"📄 Відповідь сервера:")
                print(response.text[:1000])
            
            print()
            
        except httpx.TimeoutException:
            print("❌ ТАЙМАУТ: Запит перевищив 120 секунд")
            
        except httpx.HTTPStatusError as e:
            print(f"❌ HTTP ПОМИЛКА {e.response.status_code}")
            print(f"📄 Відповідь: {e.response.text[:1000]}")
            
        except Exception as e:
            print(f"❌ НЕСПОДІВАНА ПОМИЛКА: {str(e)}")
    
    print()
    print("=" * 80)
    print("✨ Тест завершено!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_pdf_conversion())
