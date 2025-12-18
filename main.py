from pathlib import Path
from db.sqlserver import get_blobs, get_itmref_from_cblob
from domain.cblob import extract_blobs, extract_itmrefs
from fs.jpg_writer import write_jpg
from domain.sync import compare_itmrefs
from fs.images import get_jpg_names

def main():
    itmref, blob = next(extract_blobs(get_blobs()))
    out_file = Path("./out") / f"{itmref}.jpg"
    write_jpg(blob, out_file, overwrite=True)
    print("OK:", out_file)

#def test():
#    print((extract_itmrefs(get_itmref_from_cblob()))
#    print(get_jpg_names("C:/Users/FernandoSánchezRos/Desktop/local_test/img_test"))

def test():
    folder = r"\\192.168.1.82\srvfotos\Fotos\ImportadasPorNTV"
    missing, extra = compare_itmrefs(folder)

    # Ejemplo: ver algunos
    print("Primeros missing:", list(missing)[:10])


if __name__ == "__main__":
    #main()
    test()
