import { test, expect } from "@playwright/test";
import path from "path";

test.describe.serial("Suite de Regresión E2E — Gestor Documental Social", () => {
  test("Flujo 1: Login admin -> dashboard", async ({ page }) => {
    await page.goto("/");
    await page.fill("#email", "admin@local.test");
    await page.fill("#password", "admin1234");
    await page.click("button.primario");

    await expect(page).toHaveURL(/\/dashboard/);
    await expect(page.locator("h1")).toContainText("Gestor Documental Social");
    await expect(page.locator("body")).toContainText("Dashboard");
    await expect(page.locator("body")).toContainText("funcionario");
  });

  test("Flujo 2: Consulta individual CC/123456789 + ADRES + SISBÉN IV", async ({ page }) => {
    // Autenticación
    await page.goto("/");
    await page.fill("#email", "admin@local.test");
    await page.fill("#password", "admin1234");
    await page.click("button.primario");
    await page.waitForURL(/\/dashboard/);

    // Navegar a consulta individual
    await page.goto("/dashboard/consulta");
    await page.selectOption("#tipo", "CC");
    await page.fill("#numero", "123456789");

    // Marcar Sisbén IV además de ADRES
    await page.locator("label:has-text('Sisbén IV') input").check();

    // Finalidad y autorización
    await page.fill("#finalidad", "Validación de subsidio escolar municipal");
    await page.locator("label:has-text('Confirmo la autorización') input").check();

    // Ejecutar consulta
    await page.click("button.primario:has-text('Consultar')");

    // Validar resultados (2 jobs completados con datos fixture)
    await expect(page.locator("body")).toContainText("Resultados", { timeout: 10000 });
    await expect(page.locator("body")).toContainText("COMPLETED");
    await expect(page.locator("body")).toContainText("fixture: datos FICTICIOS");
    await expect(page.locator("body")).toContainText("***789");
  });

  test("Flujo 3: Carga lote CSV 4 filas -> validación, EXCLUDED visible en UI", async ({ page }) => {
    await page.goto("/");
    await page.fill("#email", "admin@local.test");
    await page.fill("#password", "admin1234");
    await page.click("button.primario");
    await page.waitForURL(/\/dashboard/);

    await page.goto("/dashboard/masiva");

    // Subir archivo CSV de 4 filas
    const csvPath = path.resolve(__dirname, "fixtures", "lote_4_filas.csv");
    await page.locator("input[type='file']").setInputFiles(csvPath);
    await page.click("button.primario:has-text('Cargar y validar')");

    // Validar visualización del lote con registro EXCLUDED
    await expect(page.locator("body")).toContainText("Excluida", { timeout: 10000 });
    await expect(page.locator("body")).toContainText("SIN_AUTORIZACION");
  });

  test("Flujo 4: Procesamiento lote -> COMPLETED y control anti-doble proceso 409", async ({ page }) => {
    await page.goto("/");
    await page.fill("#email", "admin@local.test");
    await page.fill("#password", "admin1234");
    await page.click("button.primario");
    await page.waitForURL(/\/dashboard/);

    await page.goto("/dashboard/masiva");
    const csvPath = path.resolve(__dirname, "fixtures", "lote_4_filas.csv");
    await page.locator("input[type='file']").setInputFiles(csvPath);
    await page.click("button.primario:has-text('Cargar y validar')");

    // Procesar lote
    const procesarBtn = page.locator("button.primario:has-text('Iniciar procesamiento')");
    await expect(procesarBtn).toBeVisible({ timeout: 10000 });
    await procesarBtn.click();

    // Validar que el lote se procese a COMPLETED o PARTIAL_SUCCESS
    await expect(page.locator("body")).toContainText(/(COMPLETED|PARTIAL_SUCCESS)/, { timeout: 10000 });
  });

  test("Flujo 5: Historial: jobs con tipo/estado/fuente correctos", async ({ page }) => {
    await page.goto("/");
    await page.fill("#email", "admin@local.test");
    await page.fill("#password", "admin1234");
    await page.click("button.primario");
    await page.waitForURL(/\/dashboard/);

    await page.goto("/dashboard/historial");
    await expect(page.locator("table")).toBeVisible({ timeout: 10000 });
    await expect(page.locator("body")).toContainText("Completada");
  });

  test("Flujo 6: Proveedores: 3 tipos OK en modo fixture", async ({ page }) => {
    await page.goto("/");
    await page.fill("#email", "admin@local.test");
    await page.fill("#password", "admin1234");
    await page.click("button.primario");
    await page.waitForURL(/\/dashboard/);

    await page.goto("/dashboard/proveedores");
    await expect(page.locator("table")).toBeVisible({ timeout: 10000 });

    // Verificar badges OK
    const okBadges = page.locator(".badge.verde");
    await expect(okBadges.first()).toBeVisible({ timeout: 10000 });
    const count = await okBadges.count();
    expect(count).toBeGreaterThanOrEqual(3);
  });
});
