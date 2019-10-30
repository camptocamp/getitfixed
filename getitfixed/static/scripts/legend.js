const generateLegend = features => {
  const cats = new Map()
  features.forEach(f => cats.set(f.get("category"), f.get("icon")))
  let tbody = $(".feature-legend .list-group")
  new Map([...cats.entries()].sort()).forEach(
    (icon, cat) => tbody.append(`<li class="list-group-item"><img src="${icon}"/>${cat}</li>`)
  )
}
