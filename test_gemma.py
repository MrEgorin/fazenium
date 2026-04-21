import traceback
try:
    import litert_lm
    print("litert_lm imported successfully")
    engine = litert_lm.Engine(r'c:\docs\FAZENA\fazenium\models\gemma-4-E4B-it.litertlm')
    print("Engine loaded successfully")
except Exception as e:
    print("Exception during load:")
    traceback.print_exc()
