from flask_sqlalchemy import SQLAlchemy

databaseElections = SQLAlchemy()


class ParticipantInElections(databaseElections.Model):
    __tablename__ = "participant_in_elections"

    id = databaseElections.Column(databaseElections.Integer, primary_key=True)
    participantId = databaseElections.Column(databaseElections.Integer, databaseElections.ForeignKey("participant.id"),
                                             nullable=False)
    electionsId = databaseElections.Column(databaseElections.Integer, databaseElections.ForeignKey("elections.id"),
                                           nullable=False)


class Participant(databaseElections.Model):
    __tablename__ = "participant"

    id = databaseElections.Column(databaseElections.Integer, primary_key=True)
    name = databaseElections.Column(databaseElections.String(256), nullable=False)
    individual = databaseElections.Column(databaseElections.Boolean, nullable=False)

    elections = databaseElections.relationship("Elections", secondary=ParticipantInElections.__table__,
                                               back_populates="participant")

    def __repr__(self):
        return "({}, {}".format(self.id, self.name, self.individual)


class Elections(databaseElections.Model):
    __tablename__ = "elections"

    id = databaseElections.Column(databaseElections.Integer, primary_key=True)
    start = databaseElections.Column(databaseElections.String(256), nullable=False)
    end = databaseElections.Column(databaseElections.String(256), nullable=False)
    individual = databaseElections.Column(databaseElections.Boolean, nullable=False)

    voices = databaseElections.relationship("Voice", back_populates="elections")
    participant = databaseElections.relationship("Participant", secondary=ParticipantInElections.__table__,
                                                 back_populates="elections")

    def __repr__(self):
        return "({}, {} , {}".format(self.id, self.start, self.end, self.individual)


class Voice(databaseElections.Model):
    __tablename__ = "voice"

    id = databaseElections.Column(databaseElections.Integer, primary_key=True)
    electionsId = databaseElections.Column(databaseElections.Integer, databaseElections.ForeignKey("elections.id"),
                                           nullable=False)
    guid = databaseElections.Column(databaseElections.String(36), nullable=False)
    electionOfficialJmbg = databaseElections.Column(databaseElections.String(13), nullable=False)
    valide = databaseElections.Column(databaseElections.Boolean, nullable=False)
    pollNumber = databaseElections.Column(databaseElections.Integer, nullable=False)
    reason = databaseElections.Column(databaseElections.String(256))

    elections = databaseElections.relationship("Elections", back_populates="voices")

    def __repr__(self):
        return "{}, {}, {}".format(self.id, self.electionsId, self.pollNumber)