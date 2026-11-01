(() => {
  const status = document.querySelector(".status");
  const say = (text) => {
    if (!status) return;
    status.textContent = text;
    setTimeout(() => { status.textContent = ""; }, 2500);
  };

  document.querySelector("[data-copy]")?.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(location.href);
      say("Bağlantı kopyalandı.");
    } catch {
      say("Kopyalanamadı. Adres çubuğundaki bağlantıyı kullanabilirsin.");
    }
  });

  const download = document.querySelector("[data-download]");
  download?.addEventListener("click", () => {
    const svg = document.querySelector("#buket");
    if (!svg) return;
    const xml = new XMLSerializer().serializeToString(svg);
    const url = URL.createObjectURL(new Blob([xml], { type: "image/svg+xml" }));
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement("canvas");
      canvas.width = 1200;
      canvas.height = 1560;
      const ctx = canvas.getContext("2d");
      ctx.fillStyle = "#fdf0f4";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      URL.revokeObjectURL(url);
      canvas.toBlob((blob) => {
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = `${download.dataset.name}-kasimpati.png`;
        a.click();
        say("Resim indirildi.");
      });
    };
    img.onerror = () => say("Resim oluşturulamadı.");
    img.src = url;
  });
})();
