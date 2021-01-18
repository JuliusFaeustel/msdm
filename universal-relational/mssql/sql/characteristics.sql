-- Input ohne Objektmerkmale
INSERT INTO Merkmal VALUES ('DateIn', 'Zeitstempel der Pr�fdaten', 'timestamp');
INSERT INTO Merkmal VALUES ('NR', 'Eingangsz�hler', 'int');
INSERT INTO Merkmal VALUES ('E', 'GreiferID', 'string');
INSERT INTO Merkmal VALUES ('ScanE', 'Greifer meldet keine Fehler', 'boolean');
INSERT INTO Merkmal VALUES ('MessageE', 'Eingangspr�fung Greifer meldet keine Fehler', 'boolean');
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
INSERT INTO Merkmal VALUES ('ChargeM3', 'Tr�gercharge', 'string');
INSERT INTO Merkmal VALUES ('ScanA', 'Bildanalyse druchgef�hrt', 'boolean');
INSERT INTO Merkmal VALUES ('MessungA', 'Bildanalyse meldet keine Fehler', 'boolean');
INSERT INTO Merkmal VALUES ('LagerIn', 'Eingangsladungstr�ger', 'string');
INSERT INTO Merkmal VALUES ('LagerOut', 'Ausgangsladungstr�ger', 'string');
INSERT INTO Merkmal VALUES ('Begin', 'Eingangsdatum', 'timestamp');

-- Output ohne Objektmerkmale
INSERT INTO Merkmal VALUES ('TR�GER', 'Keine Auff�lligkeiten am Tr�ger', 'boolean');
INSERT INTO Merkmal VALUES ('MAT', 'Keine Auff�lligkeiten am Material', 'boolean');
INSERT INTO Merkmal VALUES ('NAHT', 'Keine Auff�lligkeiten an der Naht', 'boolean');
INSERT INTO Merkmal VALUES ('DistMmX', 'Mittelpunktsverschiebung des Teils', 'int');
INSERT INTO Merkmal VALUES ('DistMmY', 'Mittelpunktsverschiebung des Teils', 'int');
INSERT INTO Merkmal VALUES ('AngleGrad', 'Verdrehung des Material', 'float');
INSERT INTO Merkmal VALUES ('LengthMM', 'L�nge der Naht', 'float');
INSERT INTO Merkmal VALUES ('LengthDiffMM', 'Abweichung vom Soll', 'float');
INSERT INTO Merkmal VALUES ('AngleDiffGrad', 'Abweichung der Referenzachse', 'float');
INSERT INTO Merkmal VALUES ('AxisDistMMX', 'Zentriefadenposition', 'float');
INSERT INTO Merkmal VALUES ('AxisDistMMY', 'Zentriefadenposition', 'float');
INSERT INTO Merkmal VALUES ('AxisDistMM', 'Zentriefadenposition', 'float');
INSERT INTO Merkmal VALUES ('RTotalNominal', 'Stiche pro Region', 'int');
INSERT INTO Merkmal VALUES ('RTotalCurrent', 'Stiche pro Region', 'int');
INSERT INTO Merkmal VALUES ('RCount', 'Stiche pro gez�hlt', 'int');
INSERT INTO Merkmal VALUES ('DateOut', 'Zeitstempel der Pr�fdaten', 'timestamp');

-- Objekttypen
INSERT INTO ObjektTyp VALUES ('SNR', 'Input Datens�tze');
INSERT INTO ObjektTyp VALUES ('R�ckmeldung', 'Output Datens�tze');









