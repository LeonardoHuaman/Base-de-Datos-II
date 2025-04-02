import struct
import os


RECORD_FORMAT = "5s11s20s15sif"
RECORD_SIZE = struct.calcsize(RECORD_FORMAT)
FREE_RECORD_FORMAT = "?" + RECORD_FORMAT
FREE_RECORD_SIZE = struct.calcsize(FREE_RECORD_FORMAT)

class Alumno:
    def __init__(self, codigo, nombre, apellidos, carrera, ciclo, mensualidad):
        self.codigo = codigo.encode('utf-8')[:5].ljust(5, b' ')
        self.nombre = nombre.encode('utf-8')[:11].ljust(11, b' ')
        self.apellidos = apellidos.encode('utf-8')[:20].ljust(20, b' ')
        self.carrera = carrera.encode('utf-8')[:15].ljust(15, b' ')
        self.ciclo = ciclo
        self.mensualidad = mensualidad

    def pack(self):
        return struct.pack(RECORD_FORMAT, self.codigo, self.nombre, self.apellidos, self.carrera, self.ciclo, self.mensualidad)

    @staticmethod
    def unpack(data):
        fields = struct.unpack(RECORD_FORMAT, data)
        return Alumno(fields[0].decode('utf-8').strip(), fields[1].decode('utf-8').strip(), fields[2].decode('utf-8').strip(), fields[3].decode('utf-8').strip(), fields[4], fields[5])

    def __str__(self):
        return f"{self.codigo.decode('utf-8').strip()} | {self.nombre.decode('utf-8').strip()} | {self.apellidos.decode('utf-8').strip()} | {self.carrera.decode('utf-8').strip()} | {self.ciclo} | {self.mensualidad}"


class FixedRecordMoveTheLast:
    def __init__(self, filename):
        self.filename = filename
        open(self.filename, 'ab').close()

    def add(self, record):
        with open(self.filename, 'ab') as f:
            f.write(record.pack())

    def load(self):
        records = []
        with open(self.filename, 'rb') as f:
            while True:
                data = f.read(RECORD_SIZE)
                if not data or len(data) < RECORD_SIZE:
                    break
                records.append(Alumno.unpack(data))
        return records

    def remove(self, pos):
        with open(self.filename, 'rb+') as f:
            f.seek(0, os.SEEK_END)
            filesize = f.tell()
            num_records = filesize // RECORD_SIZE

            if pos < 0 or pos >= num_records:
                print("Registro no existe")
                return

            if pos == num_records - 1:
                f.truncate((num_records - 1) * RECORD_SIZE)
            else:
                f.seek((num_records - 1) * RECORD_SIZE)
                last_record = f.read(RECORD_SIZE)
                f.seek(pos * RECORD_SIZE)
                f.write(last_record)
                f.truncate((num_records - 1) * RECORD_SIZE)

class FixedRecordFreeList:
    def __init__(self, filename):
        self.filename = filename
        open(self.filename, 'ab').close()
        self.free_list = self._build_free_list()

    def _build_free_list(self):
        free = []
        with open(self.filename, 'rb') as f:
            pos = 0
            while True:
                data = f.read(FREE_RECORD_SIZE)
                if not data or len(data) < FREE_RECORD_SIZE:
                    break
                if not struct.unpack("?", data[0:1])[0]:
                    free.append(pos)
                pos += 1
        return free

    def add(self, record):
        packed = record.pack()
        data = struct.pack("?", True) + packed
        if self.free_list:
            pos = self.free_list.pop(0)
            with open(self.filename, 'rb+') as f:
                f.seek(pos * FREE_RECORD_SIZE)
                f.write(data)
        else:
            with open(self.filename, 'ab') as f:
                f.write(data)

    def load(self):
        records = []
        with open(self.filename, 'rb') as f:
            pos = 0
            while True:
                data = f.read(FREE_RECORD_SIZE)
                if not data or len(data) < FREE_RECORD_SIZE:
                    break
                if struct.unpack("?", data[0:1])[0]:
                    records.append((pos, Alumno.unpack(data[1:])))
                pos += 1
        return records

    def remove(self, pos):
        with open(self.filename, 'rb+') as f:
            f.seek(pos * FREE_RECORD_SIZE)
            data = f.read(FREE_RECORD_SIZE)
            if not data or len(data) < FREE_RECORD_SIZE:
                print("Registro no existe")
                return
            if not struct.unpack("?", data[0:1])[0]:
                print("El registro ya está eliminado")
                return
            f.seek(pos * FREE_RECORD_SIZE)
            f.write(struct.pack("?", False))
            self.free_list.append(pos)

class FixedRecord:
    def __init__(self, filename, mode="MOVE THE LAST"):
        self.mode = mode.upper()
        self.filename = filename
        if self.mode == "MOVE THE LAST":
            self.handler = FixedRecordMoveTheLast(filename)
        elif self.mode == "FREE LIST":
            self.handler = FixedRecordFreeList(filename)
        else:
            raise ValueError("Modo de eliminación desconocido. Usa 'MOVE THE LAST' o 'FREE LIST'.")

    def add(self, record):
        self.handler.add(record)

    def load(self):
        return self.handler.load()

    def remove(self, pos):
        self.handler.remove(pos)


if __name__ == '__main__':
    filename_move = 'alumnos_move.dat'
    open(filename_move, 'wb').close()
    db_move = FixedRecord(filename_move, mode="MOVE THE LAST")
    alumno1 = Alumno("A001", "Juan", "Perez", "Inglesa", 1, 1000.0)
    alumno2 = Alumno("A002", "Ana", "Gomez", "Arquitectura", 2, 1200.0)
    alumno3 = Alumno("A003", "Luis", "Lopez", "Medicina", 3, 1500.0)
    db_move.add(alumno1)
    db_move.add(alumno2)
    db_move.add(alumno3)
    for rec in db_move.load():
        print(rec)
    db_move.remove(1)
    print("----------------------------------------------------------------")
    for rec in db_move.load():
        print(rec)