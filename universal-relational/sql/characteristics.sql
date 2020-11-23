# Input ohne Objektmerkmale
INSERT INTO Merkmal VALUES (NULL, 'DATE', 'Zeitstempel der Prüfdaten', 'timestamp');
INSERT INTO Merkmal VALUES (NULL, 'NR', 'Eingangszähler', 'int');
INSERT INTO Merkmal VALUES (NULL, 'E', 'GreiferID', 'string');
INSERT INTO Merkmal VALUES (NULL, 'ScanE', 'Greifer meldet keine Fehler', 'boolean');
INSERT INTO Merkmal VALUES (NULL, 'MessageE', 'Eingangsprüfung Greifer meldet keine Fehler', 'boolean');
INSERT INTO Merkmal VALUES (NULL, 'A2', 'Maschinenparameter', 'int');
INSERT INTO Merkmal VALUES (NULL, 'V2', 'Maschinenparameter', 'float');
INSERT INTO Merkmal VALUES (NULL, 'A1', 'Maschinenparameter', 'int');
INSERT INTO Merkmal VALUES (NULL, 'V1', 'Maschinenparameter', 'float');
INSERT INTO Merkmal VALUES (NULL, 'UseM3', 'Maschinenparameter', 'float');
INSERT INTO Merkmal VALUES (NULL, 'UseM1', 'Maschinenparameter', 'float');
INSERT INTO Merkmal VALUES (NULL, 'UseM2', 'Maschinenparameter', 'float');
INSERT INTO Merkmal VALUES (NULL, 'Delta', 'Maschinenparameter', 'float');
INSERT INTO Merkmal VALUES (NULL, 'Fehler', 'Gemeldete Fehler', 'int');
INSERT INTO Merkmal VALUES (NULL, 'Span', 'Fadenspannung nicht i.O.', 'int');
INSERT INTO Merkmal VALUES (NULL, 'ChargeM1', 'Oberfadencharge', 'string');
INSERT INTO Merkmal VALUES (NULL, 'ChargeM2', 'Unterfadencharge', 'string');
INSERT INTO Merkmal VALUES (NULL, 'ChargeM3', 'Trägercharge', 'string');
INSERT INTO Merkmal VALUES (NULL, 'ScanA', 'Bildanalyse druchgeführt', 'boolean');
INSERT INTO Merkmal VALUES (NULL, 'MessungA', 'Bildanalyse meldet keine Fehler', 'boolean');
INSERT INTO Merkmal VALUES (NULL, 'LagerIn', 'Eingangsladungsträger', 'string');
INSERT INTO Merkmal VALUES (NULL, 'LagerOut', 'Ausgangsladungsträger', 'string');
INSERT INTO Merkmal VALUES (NULL, 'Begin', 'Eingangsdatum', 'timestamp');

# Output ohne Objektmerkmale
INSERT INTO Merkmal VALUES (NULL, 'TRÄGER', 'Keine Auffälligkeiten am Träger', 'boolean');
INSERT INTO Merkmal VALUES (NULL, 'MAT', 'Keine Auffälligkeiten am Material', 'boolean');
INSERT INTO Merkmal VALUES (NULL, 'NAHT', 'Keine Auffälligkeiten an der Naht', 'boolean');
INSERT INTO Merkmal VALUES (NULL, 'DistMmX', 'Mittelpunktsverschiebung des Teils', 'int');
INSERT INTO Merkmal VALUES (NULL, 'DistMmY', 'Mittelpunktsverschiebung des Teils', 'int');
INSERT INTO Merkmal VALUES (NULL, 'AngleGrad', 'Verdrehung des Material', 'float');
INSERT INTO Merkmal VALUES (NULL, 'LengthMM', 'Länge der Naht', 'float');
INSERT INTO Merkmal VALUES (NULL, 'LengthDiffMM', 'Abweichung vom Soll', 'float');
INSERT INTO Merkmal VALUES (NULL, 'AngleDiffGrad', 'Abweichung der Referenzachse', 'float');
INSERT INTO Merkmal VALUES (NULL, 'AxisDistMMX', 'Zentriefadenposition', 'float');
INSERT INTO Merkmal VALUES (NULL, 'AxisDistMMY', 'Zentriefadenposition', 'float');
INSERT INTO Merkmal VALUES (NULL, 'AxisDistMM', 'Zentriefadenposition', 'float');
INSERT INTO Merkmal VALUES (NULL, 'RTotalNominal', 'Stiche pro Region', 'int');
INSERT INTO Merkmal VALUES (NULL, 'RTotalCurrent', 'Stiche pro Region', 'int');
INSERT INTO Merkmal VALUES (NULL, 'RCount', 'Stiche pro gezählt', 'int');
INSERT INTO Merkmal VALUES (NULL, 'Date', 'Zeitstempel der Prüfdaten', 'timestamp');

# Objekttypen
INSERT INTO ObjektTyp VALUES (NULL, 'SNR', 'Input Datensätze');
INSERT INTO ObjektTyp VALUES (NULL, 'Rückmeldung', 'Output Datensätze');











