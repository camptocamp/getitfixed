document.addEventListener('DOMContentLoaded', () => {
  let geometry_oid = issue.geometry_oid

  if (!geometry_oid) { return }

  let newIssue = issue['new']
  let params = new URL(window.location).searchParams
  let [x, y, z] = ['x', 'y', 'z'].map(_ => params.get(_))

  const getSelectedText = el => {
    const sel = el.querySelector('select')
    return sel.options[sel.selectedIndex].text
  }

  const typeEl = document.querySelector(`[class~=item-type_id]`)
  const catEl = document.querySelector(`[class~=item-category_id]`)
  const [catInput, typeInput] = [catEl, typeEl].map(el => el.querySelector('select'))

  // Update categories/types on moveend
  let controller
  let catId, typeId
  let map, layer
  let categories

  // Build <option> element from config obj
  const buildOption = (obj, selected) => {
    const option = document.createElement('option')
    option.value = obj.id
    if (obj.wms_layer) {
      option.setAttribute('data-wms', obj.wms_layer)
    }
    option.innerText = obj.label
    if (obj.id == selected) option.selected = 'selected'
    return option
  }

  // Fetch categories & update form fields
  const updateCategories = () => {
    if (controller) { controller.abort() }
    controller = new AbortController()
    fetch(issue.categories_url, { signal: controller.signal })
      .then(r => r.json())
      .then(cats => {

        const _ = JSON.stringify
        if (_(cats.map(c => c.id)) == _(Array.from(catInput.options).map(n => parseInt(n.value)))) {
          // Identical possible values
          return
        }

        // Store categories
        categories = cats

        // store selected values
        catId = catInput.value

        // Empty categories list
        catInput.innerHTML = ''
        // Fill & restore values if possible
        cats.forEach(c => catInput.appendChild(buildOption(c, catId)))
        catInput.dispatchEvent(new Event('change', { bubbles: true }))
      })
      .catch(err => {
        if (err.name === 'AbortError') {
          console.log('Fetch aborted');
        } else {
          console.error(err);
        }
      })
  }
  document.querySelector(`#${geometry_oid}`).addEventListener('input', updateCategories)

  catInput.addEventListener('change', () => {
    // store selected value
    typeId = typeInput.value

    // Update options
    const types = categories.find(e => e.id == catInput.value).types
    typeInput.innerHTML = ''
    types.forEach(o => typeInput.appendChild(buildOption(o, typeId)))

    // Autoselect first if no one selected
    if (!typeInput.querySelector('[selected=selected]')) {
      typeInput.options[0].selected = 'selected'
      typeInput.dispatchEvent(new Event('change', { bubbles: true }))
    }
  })

  typeInput.addEventListener('change', () => {
    if (!typeInput.value || typeId === typeInput.value) { return } // Avoid flickering

    //store type value
    typeId = typeInput.value

    // Update WMS layer in map
    if (layer) {
      map.removeLayer(layer)
      layer = undefined
    }
    let option = typeInput.options[typeInput.selectedIndex]
    if (!option.getAttribute('data-wms')) return
    layer = c2cgeoform.addLayer(geometry_oid, {
      type_: 'WMS',
      url: option.getAttribute('data-wms')
    })
  })

  deform.addCallback(geometry_oid, function () {
    // Recenter on feature or query params
    map = c2cgeoform.getObjectMap(geometry_oid)
    let features = map.getLayers().item(1).getSource().getFeatures()
    if (features.length === 0) {
      if (x && y && z) {
        map.getView().setCenter([params.get('x'), params.get('y')].map(parseFloat))
        map.getView().setZoom(parseFloat(params.get('z')))
      }
    } else {
      map.getView().fit(features[0].getGeometry().getExtent(), {
        maxZoom: 18
      })
    }

    if (!window.matchMedia('(max-width: 576px)').matches || !newIssue) { return }

    // On mobile move geometry/cat/type on a temporary focused subform
    document.body.classList.add('focused')
    window.scrollTo(0, 0)
    let focus = document.querySelector('.focus')
    let mapEl = document.querySelector(`#item-${geometry_oid}`)
    focus.append(mapEl)

    let subform = document.querySelector('.subform')
    let fieldset = document.querySelector('fieldset')
    subform.prepend(typeEl)
    subform.prepend(catEl)
    map.updateSize()

    // When validating subform, move back inputs into the form,
    // turning those 3 fields read-only
    focus.querySelector('.next').addEventListener('click', () => {
      document.body.classList.remove('focused')
      ;[typeEl, catEl, mapEl].forEach(e => (fieldset.prepend(e)))
      c2cgeoform.setReadOnly(geometry_oid)
      mapEl.querySelector('label').innerText = getSelectedText(catEl) + ' / ' + getSelectedText(typeEl)
      ;[typeEl, catEl, focus].forEach(e => {e.style.display = 'none'})
      mapEl.scrollIntoView({ behavior: 'smooth' })
    })
  })
})
