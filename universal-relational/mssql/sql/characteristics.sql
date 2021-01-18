-- Input ohne Objektmerkmale
INSERT INTO Merkmal VALUES ('DateIn', 'Zeitstempel der Prüfdaten', 'timestamp');
INSERT INTO Merkmal VALUES ('NR', 'Eingangszähler', 'int');
INSERT INTO Merkmal VALUES ('E', 'GreiferID', 'string');
INSERT INTO Merkmal VALUES ('ScanE', 'Greifer meldet keine Fehler', 'boolean');
INSERT INTO Merkmal VALUES ('MessageE', 'Eingangsprüfung Greifer meldet keine Fehler', 'boolean');
INSERT INTO Merkmal VALUES ('A2', 'Maschinenparameter', 'int');
INSERT INTO Merkmal VALUES ('V2', 'Maschinenparameter', 'float');
INSERT INTO Merkmal VALUES ('A1', 'Maschinenparameter', 'int');
INSERT INTO Merkmal VALUES ('V1', 'Maschinenparameter', 'float');
INSERT INTO Merkmal VALUES ('UseM3', 'Maschinenparameter', 'float');
INSERT INTO Merkmal VALUES ('UseM1', 'Maschinenparameter', 'float');
INSERT INTO Merkmal VALUES ('UseM2', 'Maschinenparameter', 'float');
INSERT INTO Merkmal VALUES ('Delta', 'Maschinenparameter', 'float');
INSERT INTO Merkmal VALUES ('Fehler', 'Gemeldete Fehler', 'int');
INSERT INTO Merkmal VALUES ('Span', 'Fadenspannung nicht i.O.', 'int');
INSERT INTO Merkmal VALUES ('ChargeM1', 'Oberfadencharge', 'string');
INSERT INTO Merkmal VALUES ('ChargeM2', 'Unterfadencharge', 'string');
INSERT INTO Merkmal VALUES ('ChargeM3', 'Trägercharge', 'string');
INSERT INTO Merkmal VALUES ('ScanA', 'Bildanalyse druchgeführt', 'boolean');
INSERT INTO Merkmal VALUES ('MessungA', 'Bildanalyse meldet keine Fehler', 'boolean');
INSERT INTO Merkmal VALUES ('LagerIn', 'Eingangsladungsträger', 'string');
INSERT INTO Merkmal VALUES ('LagerOut', 'Ausgangsladungsträger', 'string');
INSERT INTO Merkmal VALUES ('Begin', 'Eingangsdatum', 'timestamp');

-- Output ohne Objektmerkmale
INSERT INTO Merkmal VALUES ('TRÄGER', 'Keine Auffälligkeiten am Träger', 'boolean');
INSERT INTO Merkmal VALUES ('MAT', 'Keine Auffälligkeiten am Material', 'boolean');
INSERT INTO Merkmal VALUES ('NAHT', 'Keine Auffälligkeiten an der Naht', 'boolean');
INSERT INTO Merkmal VALUES ('DistMmX', 'Mittelpunktsverschiebung des Teils', 'int');
INSERT INTO Merkmal VALUES ('DistMmY', 'Mittelpunktsverschiebung des Teils', 'int');
INSERT INTO Merkmal VALUES ('AngleGrad', 'Verdrehung des Material', 'float');
INSERT INTO Merkmal VALUES ('LengthMM', 'Länge der Naht', 'float');
INSERT INTO Merkmal VALUES ('LengthDiffMM', 'Abweichung vom Soll', 'float');
INSERT INTO Merkmal VALUES ('AngleDiffGrad', 'Abweichung der Referenzachse', 'float');
INSERT INTO Merkmal VALUES ('AxisDistMMX', 'Zentriefadenposition', 'float');
INSERT INTO Merkmal VALUES ('AxisDistMMY', 'Zentriefadenposition', 'float');
INSERT INTO Merkmal VALUES ('AxisDistMM', 'Zentriefadenposition', 'float');
INSERT INTO Merkmal VALUES ('RTotalNominal', 'Stiche pro Region', 'int');
INSERT INTO Merkmal VALUES ('RTotalCurrent', 'Stiche pro Region', 'int');
INSERT INTO Merkmal VALUES ('RCount', 'Stiche pro gezählt', 'int');
INSERT INTO Merkmal VALUES ('DateOut', 'Zeitstempel der Prüfdaten', 'timestamp');

-- Objekttypen
INSERT INTO ObjektTyp VALUES ('SNR', 'Input Datensätze');
INSERT INTO ObjektTyp VALUES ('Rückmeldung', 'Output Datensätze');









