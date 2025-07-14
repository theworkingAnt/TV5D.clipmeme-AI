# Meme caption via fallback
if action in ["Meme", "Both"]:
    st.write("### Suggested Meme Captions:")

    # Basic Tagalog keyword matching for memes
    subtitle_lower = subtitle.lower()

    captions = []
    if any(word in subtitle_lower for word in ["mahal", "pag-ibig", "iniwan", "bakit"]):
        captions.append("“Minsan kahit mahal mo, kailangan mong bitawan 💔”")
        captions.append("“Lagi na lang akong option, kailan ako magiging priority?”")
    elif any(word in subtitle_lower for word in ["suntok", "galit", "higanti", "patay"]):
        captions.append("“'Wag mo kong subukan kung ayaw mong pagsisihan.”")
        captions.append("“Revenge is a dish best served mainit pa rin!”")
    elif any(word in subtitle_lower for word in ["tawa", "loko", "sabaw", "asaran"]):
        captions.append("“Pagod na ko sa buhay, pero go lang. Char!”")
        captions.append("“Huwag seryoso, baka masaktan. Meme lang to!”")
    else:
        captions.append("“When life gives you teleserye... make memes.”")
        captions.append("“Ganito kami sa TV5. Hugot, iyak, tawa – ulit!”")

    # Show results
    for i, cap in enumerate(captions[:3], 1):
        st.markdown(f"**{i}.** {cap}")
