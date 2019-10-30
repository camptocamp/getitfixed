const generateLegend = function(features) {
  const results = []
  const map = new Map()
  for (const feature of features) {
    let category = feature.get("category")
    if (!map.has(category)) {
      map.set(category, true)
      results.push({
        cat: category,
        icon: feature.get("icon")
      })
    }
  }
  results.sort((a, b) => (a.cat > b.cat ? 1 : b.cat > a.cat ? -1 : 0))
  let tbody = $("#feature-legend .list-group")
  $.each(results, function(i, result) {
    let li = $("<li>")
    $("<li>", { class: "list-group-item" })
      .html(result["cat"])
      .append($("<img>").attr("src", result["icon"]))
      .appendTo(li)
      .appendTo(li)

    tbody.append(li)
  })
}
