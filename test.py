def top6of8(listof8):
    assert len(listof8)==8, "Gotta send 8"
    z=sorted(listof8,reverse=True)
    return z[0] + z[1] + z[2] + z[3] + z[4] + z[5]

top60f8([4,6,4,7,2,9,4,1])
