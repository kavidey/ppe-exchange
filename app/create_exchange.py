from flask import render_template
from app import app
from app.models import User, PPE, Hospital, Wants, Has, Exchanges, Exchange

def create_exchange():
    
    haves = Has.query.all()
    for have in haves:
        # store have.id, have.hospital_id, have.ppe_id, have.count
        print("have" + have.id+", "+have.hospital_id+", "+have.ppe_id +", "+have.count)
    
    wants = Wants.query.all()
    for want in wants:
        # store want.id, want.hospital_id, want.ppe_id, want.count
        print("want" + want.id+", "+want.hospital_id+", "+want.ppe_id +", "+want.count)

    ppes = PPE.query.all()
    for ppe in ppes:
        haves = Has.query(ppe_id=ppe.id)
        wants = Wants.query(ppe_id=ppe.id)

        have_total = 0
        want_total = 0
        for have in haves:
            have_total = have_total + have.count
        for want in wants:
            want_total = want_total + want.count
        
        # enough supply to meet demand
        if want_total < have_total:
            ratio = want_total/have_total
            for have in haves:
                send_amount = int(have.count * ratio)
                for want in wants:
                    sending = min(send_amount,want.count)
                    # create exchange moving sending amount of ppe.id from have.hospital_id to want.hospital_id
                    send_amount = send_amount - sending
                    want.count = want.count - sending
        # not enough supply to meet demand
        else:
            ratio = have_total/want_total
            for want in wants:
                want.count = want.count * ratio

            for have in haves:
                for want in wants:
                    sending = min(have.count,want.count)
                    # create exchange moving have.count amount of ppe.id from have.hospital_id to want.hospital_id
                    send_amount = send_amount - sending
                    want.count = want.count - sending

    # update credits and has and wants

    # loop through created exchanges
        # transfer = exchange.count

        # first credits
        # hosptial1 = Hospital.query.filter_by(id=exchange.h1).first()
        # hosptial1.credits = hosptial1.credits + transfer
        #
        # hosptial2 = Hospital.query.filter_by(id=exchange.h2).first()
        # hosptial2.credits = hosptial2.credits - transfer

        # then has
        # has1 = Has.query.filter_by(hospital_id=exchange.h1, ppe_id=exchange.ppe_id)
        # has1.count = has1.count - transfer
        
        # then want
        # want2 = Wants.query.filter_by(hospital_id=exchange.h2, ppe_id=exchange.ppe_id)
        # want2.count = want2.count - transfer