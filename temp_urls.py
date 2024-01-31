Hello, atous!
Hello,main!
@main.route('bases_minimums_de_cfe_un_principearticle1')
def bases_minimums_de_cfe_un_principearticle1():
    return render_template('/medeo/templates/news/[fiche finances] fiscalité/bases_minimums_de_cfe_un_principearticle1.html', title='News Template')

@main.route("/bases_minimums_de_cfe_un_principe")
def bases_minimums_de_cfe_un_principe():
    return render_template("/news/[fiche finances] fiscalité/bases_minimums_de_cfe_un_principe.html", title="News Template")
