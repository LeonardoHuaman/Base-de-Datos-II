// Integrantes: Leonardo Fabian Huaman Casma
//             Johar Jared Barzola Estrella


#include <iostream>
#include <fstream>
#include <vector>
#include <string>

using namespace std;

struct Registro {
    string codigo;
    int ciclo;
    double mensualidad;
    string observaciones;
};

struct Metadata {
    long position;
    long size;
};

const string DATA_FILE = "registros.dat";
const string META_FILE = "metadata.dat";

void writeString(ofstream &file, const string &str) {
    size_t len = str.size();
    file.write((char*)&len, sizeof(len));
    file.write(str.c_str(), len);
}

string readString(ifstream &file) {
    size_t len;
    file.read((char*)&len, sizeof(len));
    char* buffer = new char[len + 1];
    file.read(buffer, len);
    buffer[len] = '\0';
    string str(buffer);
    delete[] buffer;
    return str;
}

void add(const Registro& record) {
    ofstream file(DATA_FILE, ios::binary | ios::app);
    ofstream metaFile(META_FILE, ios::binary | ios::app);
    if (!file || !metaFile) {
        cerr << "Error al abrir archivos." << endl;
        return;
    }
    
    long pos = static_cast<long>(file.tellp());
    
    writeString(file, record.codigo);
    file.write((char*)&record.ciclo, sizeof(int));
    file.write((char*)&record.mensualidad, sizeof(double));
    writeString(file, record.observaciones);
    
    long size = static_cast<long>(file.tellp()) - pos;
    Metadata meta = {pos, size};
    metaFile.write((char*)&meta, sizeof(Metadata));
    
    file.close();
    metaFile.close();
}

vector<Registro> load() {
    ifstream file(DATA_FILE, ios::binary);
    ifstream metaFile(META_FILE, ios::binary);
    
    if (!file || !metaFile) {
        cerr << "Error al abrir archivos." << endl;
        return {};
    }

    vector<Registro> records;
    vector<long> validPositions;
    Metadata meta;

    // Leer metadatos y obtener posiciones válidas
    while (metaFile.read((char*)&meta, sizeof(Metadata))) {
        if (meta.position != -1) { // Solo agregar posiciones válidas
            validPositions.push_back(meta.position);
        }
    }

    for (long pos : validPositions) {
        file.seekg(pos, ios::beg);
        Registro record;
        record.codigo = readString(file);
        file.read((char*)&record.ciclo, sizeof(int));
        file.read((char*)&record.mensualidad, sizeof(double));
        record.observaciones = readString(file);
        records.push_back(record);
    }

    file.close();
    metaFile.close();
    return records;
}

void remove(long pos) {
    fstream metaFile(META_FILE, ios::binary | ios::in | ios::out);
    if (!metaFile) {
        cerr << "Error al abrir archivo de metadatos." << endl;
        return;
    }

    Metadata meta;
    long offset = 0;

    while (metaFile.read((char*)&meta, sizeof(Metadata))) {
        if (meta.position == pos) {
            meta.position = -1; // Marcar como eliminado
            metaFile.seekp(offset, ios::beg);
            metaFile.write((char*)&meta, sizeof(Metadata));
            break;
        }
        offset += sizeof(Metadata);
    }

    metaFile.close();
}

int main() {
    Registro r1 = {"A123", 2, 450.75, "Pago puntual"};
    Registro r2 = {"B456", 3, 500.50, "Pago atrasado"};

    add(r1);
    add(r2);

    ifstream metaFile(META_FILE, ios::binary);
    vector<Metadata> metadata;
    
    if (metaFile) {
        Metadata meta;
        while (metaFile.read((char*)&meta, sizeof(Metadata))) {
            metadata.push_back(meta);
        }
        metaFile.close();
    }

    cout << "\nAntes de eliminar\n";
    vector<Registro> registros = load();
    for (const auto& r : registros) {
        cout << "Codigo: " << r.codigo << ", Ciclo: " << r.ciclo
             << ", Mensualidad: " << r.mensualidad
             << ", Observaciones: " << r.observaciones << endl;
    }

    if (!metadata.empty() && metadata[0].position != -1) {
        remove(metadata[0].position);
        cout << "\nRegistro con posicion " << metadata[0].position << " eliminado.\n";
    }

    cout << "\n Después de eliminar n";
    registros = load();
    for (const auto& r : registros) {
        cout << "Codigo: " << r.codigo << ", Ciclo: " << r.ciclo
             << ", Mensualidad: " << r.mensualidad
             << ", Observaciones: " << r.observaciones << endl;
    }

    return 0;
}
